# Autoclip global plugin
# A part of the Autoclip add-on for NVDA
# Copyright (C) 2023 Mazen Alharbi
# This file is covered by the GNU General Public License Version 2.
# See the file LICENSE for more details.
# If the LICENSE file is not available, you can find the  GNU General Public License Version 2 at this link:
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import time

import wx

import addonHandler
import config
import core
import globalPluginHandler
import globalVars
import gui
import gui.guiHelper
import queueHandler
import scriptHandler
import speech
import ui
from logHandler import log

from . import winclip

addonHandler.initTranslation()

min_chunk_size = 100
DEFAULT_CHUNK_SIZE = 500
DEFAULT_SPLIT_AT_WORD_BOUNDS = True
DEFAULT_MAX_LENGTH = 15000
DEFAULT_DEBOUNCE_DELAY = 100
DEFAULT_INTERRUPT_DELAY = 50


class ClipboardWatcher:
    def __init__(self):
        self.state = False
        self.window = None
        self.last_time = 0  # last time a clipboard notification was sent
        self.last_data = ""  # last text of a clipboard notification
        self.load_config()

    def load_config(self):
        conf = config.conf["autoclip"]
        self.interrupt = conf["interrupt"]
        self.chunk_size = conf["chunkSize"]
        self.split_at_word = conf["splitAtWordBounds"]
        self.max_length = conf["maxLength"]
        self.debounce_delay = conf["debounceDelay"] / 1000
        self.interrupt_delay = conf["interruptDelay"] / 1000

    @staticmethod
    def split_text(text, chunk_size, split_at_word):
        length = len(text)
        if not text or length <= chunk_size or not chunk_size or chunk_size < min_chunk_size:
            return [text]

        chunks = []
        index = 0
        while index < length:
            next_index = min(index + chunk_size, length)
            chunk = text[index:next_index]
            if next_index >= length or not split_at_word or chunk.endswith(" "):
                chunks.append(chunk)
                index = next_index
            else:
                last_space = chunk.rfind(" ")
                if last_space > 1:
                    chunks.append(chunk[:last_space])
                    index += last_space + 1
                else:
                    chunks.append(chunk)
                    index = next_index
        return chunks

    def message_text(self, text, interrupt=False):
        if interrupt:
            speech.cancelSpeech()

        if len(text) > self.chunk_size:
            chunks = ClipboardWatcher.split_text(text, self.chunk_size, self.split_at_word)
            for chunk in chunks:
                ui.message(chunk)
        else:
            ui.message(text)

    def start(self):
        self.window = winclip.ClipboardMessageWindow()
        self.window.on_clipboard_update = self.notify
        self.state = True

    def stop(self):
        self.window.destroy()
        self.window = None
        self.state = False

    def notify(self):
        with winclip.clipboard(self.window.hwnd):
            data = winclip.get_clipboard_data()
        current_time = time.monotonic()
        if data and not data.isspace() and len(data) < self.max_length:
            if self.last_data == data and (current_time - self.last_time) < self.debounce_delay:
                self.last_time = current_time()
                return
            should_interrupt = False
            if self.interrupt and (current_time - self.last_time) > self.interrupt_delay:
                should_interrupt = True
            queueHandler.queueFunction(
                queueHandler.eventQueue, self.message_text, data, should_interrupt
            )
            self.last_data = data
            self.last_time = current_time


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Autoclip")

    def __init__(self):
        super().__init__()
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
        conf = config.conf["autoclip"]
        if self.watcher:  # reload configuration encase settings changed
            self.watcher.load_config()

        if conf["rememberState"]:
            value = conf["automaticClipboardReading"]
            if value and not self.watcher:
                self.enable()
            elif not value and self.watcher:
                self.disable()

        if conf["showInToolsMenu"] and not self.menuItem:
            self.addMenuItem()
        elif not conf["showInToolsMenu"] and self.menuItem:
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
        super().terminate()
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
    "chunkSize": f"integer(default={DEFAULT_CHUNK_SIZE})",
    "maxLength": f"integer(default={DEFAULT_MAX_LENGTH})",
    "splitAtWordBounds": f"boolean(default={str(DEFAULT_SPLIT_AT_WORD_BOUNDS).lower()})",
    "debounceDelay": f"integer(default={DEFAULT_DEBOUNCE_DELAY})",
    "interruptDelay": f"integer(default={DEFAULT_INTERRUPT_DELAY})",
}

config.conf.spec["autoclip"] = confspec


class AutoclipSettings(gui.settingsDialogs.SettingsPanel):
    title = _("Autoclip")

    def makeSettings(self, panelSizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=panelSizer)

        self.interruptCB = sHelper.addItem(
            wx.CheckBox(self, label=_("&Interrupt before speaking the clipboard"))
        )

        self.rememberCB = sHelper.addItem(
            wx.CheckBox(
                self,
                label=_(
                    "&Remember automatic clipboard reading after NVDA restart. Required for use in configuration profiles"
                ),
            )
        )

        self.showCB = sHelper.addItem(wx.CheckBox(self, label=_("&Show in the NVDA tools menu")))

        # Advanced settings
        gboxSizer = wx.StaticBoxSizer(wx.VERTICAL, self, _("Advanced Settings"))
        gbox = gboxSizer.GetStaticBox()
        gHelper = gui.guiHelper.BoxSizerHelper(gbox, sizer=gboxSizer)

        self.chunkSizeEdit = gHelper.addLabeledControl(
            _(
                "Split text above this length to segments spoken separately (number under 100 to disable):"
            ),
            wx.SpinCtrl,
            min=0,
            max=10000,
        )

        self.splitAtWordCB = gHelper.addItem(
            wx.CheckBox(
                gbox, label=_("When splitting text, try to split segments at word boundaries")
            )
        )

        self.maxLengthEdit = gHelper.addLabeledControl(
            _("Maximum text length to speak (characters):"),
            wx.SpinCtrl,
            min=1000,
            max=1000000,
        )

        self.debounceDelayEdit = gHelper.addLabeledControl(
            _(
                "Debounce Delay to not speaking a clipboard update with the same text (milliseconds) (0 to disable):"
            ),
            wx.SpinCtrl,
            min=0,
            max=30000,
        )

        self.interruptDelayEdit = gHelper.addLabeledControl(
            _(
                "Minimum delay between speech interrupts (milliseconds) (0 to disable and to always interrupt):"
            ),
            wx.SpinCtrl,
            min=0,
            max=5000,
        )

        self.restoreDefaultsButton = gHelper.addItem(
            wx.Button(gbox, label=_("Restore advanced settings to &defaults"))
        )
        self.restoreDefaultsButton.Bind(wx.EVT_BUTTON, self.onRestoreDefaults)
        sHelper.addItem(gHelper)

        self.loadValues()

    def loadValues(self):
        conf = config.conf["autoclip"]
        self.interruptCB.SetValue(conf["interrupt"])
        self.rememberCB.SetValue(conf["rememberState"])
        self.showCB.SetValue(conf["showInToolsMenu"])
        self.chunkSizeEdit.SetValue(conf["chunkSize"])
        self.splitAtWordCB.SetValue(conf["splitAtWordBounds"])
        self.maxLengthEdit.SetValue(conf["maxLength"])
        self.debounceDelayEdit.SetValue(conf["debounceDelay"])
        self.interruptDelayEdit.SetValue(conf["interruptDelay"])

    def onRestoreDefaults(self, evt):
        self.chunkSizeEdit.SetValue(DEFAULT_CHUNK_SIZE)
        self.splitAtWordCB.SetValue(DEFAULT_SPLIT_AT_WORD_BOUNDS)
        self.maxLengthEdit.SetValue(DEFAULT_MAX_LENGTH)
        self.debounceDelayEdit.SetValue(DEFAULT_DEBOUNCE_DELAY)
        self.interruptDelayEdit.SetValue(DEFAULT_INTERRUPT_DELAY)

    def onSave(self):
        conf = config.conf["autoclip"]
        conf["interrupt"] = self.interruptCB.IsChecked()
        conf["rememberState"] = self.rememberCB.IsChecked()
        conf["showInToolsMenu"] = self.showCB.IsChecked()
        conf["chunkSize"] = self.chunkSizeEdit.GetValue()
        conf["splitAtWordBounds"] = self.splitAtWordCB.IsChecked()
        conf["maxLength"] = self.maxLengthEdit.GetValue()
        conf["debounceDelay"] = self.debounceDelayEdit.GetValue()
        conf["interruptDelay"] = self.interruptDelayEdit.GetValue()
        plugin = next(
            (p for p in globalPluginHandler.runningPlugins if type(p) is GlobalPlugin), None
        )
        if plugin:
            queueHandler.queueFunction(queueHandler.eventQueue, plugin.onConfigInit)
        else:
            log.warning("Unable to get plugin to apply configuration")
