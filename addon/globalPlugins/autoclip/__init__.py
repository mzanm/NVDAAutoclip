# Autoclip global plugin
# A part of the Autoclip add-on for NVDA
# Copyright (C) 2023 Mazen Alharbi
# This file is covered by the GNU General Public License Version 2.
# See the file LICENSE for more details.
# If the LICENSE file is not available, you can find the  GNU General Public License Version 2 at this link:
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import ctypes
import time
from ctypes import wintypes

import wx

import addonHandler
import config
import core
import globalPluginHandler
import globalVars
import gui
import queueHandler
import scriptHandler
import speech
import ui
from logHandler import log

from . import winclip

addonHandler.initTranslation()


class ClipboardWatcher:
    def __init__(self):
        self.state = False
        self.last_time = 0  # last time a clipboard notification was sent
        self.last_data = ""  # last text of a clipboard notification
        self.winclip = winclip.win32clip()
        self.hwnd = self.winclip.CreateWindow(
            0,
            "STATIC",
            None,
            0,
            0,
            0,
            0,
            0,
            winclip.HWND_MESSAGE,
            None,
            self.winclip.GetModuleHandle(None),
            None,
        )
        log.debug("created window %d", self.hwnd)

    @staticmethod
    def message_text(text, interrupt=False):
        if interrupt:
            speech.cancelSpeech()
        if len(text) > 1000:
            chunks = []
            for i in range(0, len(text), 500):
                chunks.append(text[i : i + 500])
            for chunk in chunks:
                ui.message(chunk)
        else:
            ui.message(text)

    def start(self):
        @ctypes.WINFUNCTYPE(
            ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
        )
        def wndproc(hwnd, msg, wparam, lparam):
            if msg == winclip.WM_CLIPBOARDUPDATE:
                try:
                    self.notify()
                    return 0
                except Exception:
                    log.exception("Error in window proc notify")
            return self.winclip.DefWindowProc(hwnd, msg, wparam, lparam)

        self.proc = wndproc
        self.oldProc = self.winclip.SetWindowLong(
            self.hwnd, winclip.GWL_WNDPROC, ctypes.cast(self.proc, ctypes.c_void_p)
        )

        res = self.winclip.AddClipboardFormatListener(self.hwnd)
        log.debug("add format listener %d", res)
        self.state = True

    def stop(self):
        self.winclip.RemoveClipboardFormatListener(self.hwnd)
        self.winclip.SetWindowLong(self.hwnd, winclip.GWL_WNDPROC, self.oldProc)
        self.winclip.DestroyWindow(self.hwnd)
        self.proc = None
        self.oldProc = None
        self.state = False
        self.last_time = 0
        self.last_data = ""

    def notify(self):
        with self.winclip.clipboard(self.hwnd):
            data = self.winclip.get_clipboard_data()
            if data and not data.isspace() and len(data) < 15000:
                if self.last_data == data and time.monotonic() - self.last_time < 0.1:
                    self.last_time = time.monotonic()
                    return
                interrupt = False
                if (
                    config.conf["autoclip"]["interrupt"]
                    and time.monotonic() - self.last_time > 0.05
                ):
                    interrupt = True
                queueHandler.queueFunction(
                    queueHandler.eventQueue, ClipboardWatcher.message_text, data, interrupt
                )
                self.last_data = data
                self.last_time = time.monotonic()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Autoclip")

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.watcher = None
        self.menuItem = None
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(AutoclipSettings)
        core.postNvdaStartup.register(self.onConfigInit)
        config.post_configProfileSwitch.register(self.onConfigInit)

    def onConfigInit(self):
        # called at NVDA startup if the add-on is configured to remember the state is enabled or disabled,
        #  as well as when a configuration profile is switched.
        if globalVars.appArgs.secure:
            return
        if config.conf["autoclip"]["rememberState"]:
            value = config.conf["autoclip"]["automaticClipboardReading"]
            if value and not self.watcher:
                self.enable()
            elif not value and self.watcher:
                self.disable()

        if config.conf["autoclip"]["showInToolsMenu"] and not self.menuItem:
            self.addMenuItem()
        elif not config.conf["autoclip"]["showInToolsMenu"] and self.menuItem:
            self.deleteMenuItem()

    @scriptHandler.script(
        description=_("Toggles Autoclip, Automatic clipboard reading."),
        category=_("Autoclip"),
        gesture="kb:NVDA+control+shift+k",
        allowInSleepMode=True,
    )
    def script_toggleAutoclip(self, gesture):
        self.toggle()

    @scriptHandler.script(
        description=_("Toggles if Autoclip should interrupt speech before speaking the clipboard"),
        category=_("Autoclip"),
    )
    def script_toggleInterrupt(self, gesture):
        if not config.conf["autoclip"]["interrupt"]:
            config.conf["autoclip"]["interrupt"] = True
            ui.message(_('Enabled "Interrupt before speaking the clipboard"'))
        else:
            config.conf["autoclip"]["interrupt"] = False
            ui.message(_('Disabled "Interrupt before speaking the clipboard"'))

    def enable(self):
        if self.watcher:
            return
        self.watcher = ClipboardWatcher()
        self.watcher.start()
        log.debug("Enabled")
        if self.menuItem:
            self.menuItem.Check()

    def disable(self):
        if not self.watcher:
            return
        if self.watcher.state:
            self.watcher.stop()
        self.watcher = None
        log.debug("Disabled")
        if self.menuItem:
            self.menuItem.Check(False)

    def toggle(self):
        if not self.watcher:
            self.enable()
            config.conf["autoclip"]["automaticClipboardReading"] = True
            ui.message(_("Enabled Automatic Clipboard Reading."))
        else:
            self.disable()
            config.conf["autoclip"]["automaticClipboardReading"] = False
            ui.message(_("Disabled Automatic Clipboard Reading."))

    def addMenuItem(self):
        if self.menuItem:
            return
        self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
        self.menuItem = self.toolsMenu.AppendCheckItem(
            wx.ID_ANY,
            _("&Automatic clipboard reading"),
            _("Toggles Autoclip, Automatic clipboard reading."),
        )
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda event: self.toggle(), self.menuItem)
        if self.watcher and self.watcher.state:
            self.menuItem.Check()

    def deleteMenuItem(self):
        if not self.menuItem:
            return
        self.toolsMenu.Delete(self.menuItem)
        self.menuItem = None
        self.toolsMenu = None

    def terminate(self):
        super(GlobalPlugin, self).terminate()
        self.disable()
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(AutoclipSettings)
        self.deleteMenuItem()
        core.postNvdaStartup.unregister(self.onConfigInit)
        config.post_configProfileSwitch.unregister(self.onConfigInit)


confspec = {
    "interrupt": "boolean(default=false)",
    "rememberState": "boolean(default=false)",
    "automaticClipboardReading": "boolean(default=false)",
    "showInToolsMenu": "boolean(default=true)",
}

config.conf.spec["autoclip"] = confspec


class AutoclipSettings(gui.settingsDialogs.SettingsPanel):
    title = _("Autoclip")

    def makeSettings(self, panelSizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=panelSizer)
        self.interruptCB = sHelper.addItem(
            wx.CheckBox(self, label=_("Always &Interrupt before speaking the clipboard"))
        )

        self.rememberCB = sHelper.addItem(
            wx.CheckBox(
                self,
                label=_(
                    "&Remember automatic clipboard reading after  NVDA restart. Required for use in configuration profiles"
                ),
            )
        )

        self.showCB = sHelper.addItem(wx.CheckBox(self, label=_("&Show in the NVDA tools menu")))

        self.interruptCB.SetValue(config.conf["autoclip"]["interrupt"])
        self.rememberCB.SetValue(config.conf["autoclip"]["rememberState"])
        self.showCB.SetValue(config.conf["autoclip"]["showInToolsMenu"])

    def onSave(self):
        config.conf["autoclip"]["interrupt"] = self.interruptCB.IsChecked()
        config.conf["autoclip"]["rememberState"] = self.rememberCB.IsChecked()
        config.conf["autoclip"]["showInToolsMenu"] = self.showCB.IsChecked()
        try:
            plugin = next(p for p in globalPluginHandler.runningPlugins if type(p) is GlobalPlugin)
        except StopIteration:
            log.exception("Unable to get plugin to apply configuration")
            plugin = None
        if plugin:
            queueHandler.queueFunction(queueHandler.eventQueue, plugin.onConfigInit)
