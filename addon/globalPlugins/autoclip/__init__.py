import ctypes
from ctypes import wintypes

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
import wx
from logHandler import log

from . import winclip

addonHandler.initTranslation()


class ClipboardWatcher:
	def __init__(self):
		self.state = False
		self.hwnd = winclip.CreateWindow(
			0,
			"STATIC",
			None,
			0,
			0,
			0,
			0,
			0,
			-3,
			None,
			ctypes.windll.kernel32.GetModuleHandleW(None),
			None,
		)
		log.debug(f"created window {self.hwnd}")

	def start(self):
		@ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
		def wndproc(hwnd, msg, wparam, lparam):
			if msg == winclip.WM_CLIPBOARDUPDATE:
				queueHandler.queueFunction(queueHandler.eventQueue, self.notify)
				return 0
			return winclip.DefWindowProc(hwnd, msg, wparam, lparam)

		self.proc = wndproc
		self.oldProc = winclip.SetWindowLong(
			self.hwnd, winclip.GWL_WNDPROC, ctypes.cast(self.proc, ctypes.c_void_p)
		)

		res = winclip.AddClipboardFormatListener(self.hwnd)
		log.debug(f"add format listener {res}")
		self.state = True

	def stop(self):
		winclip.RemoveClipboardFormatListener(self.hwnd)
		winclip.SetWindowLong(self.hwnd, winclip.GWL_WNDPROC, self.oldProc)
		winclip.DestroyWindow(self.hwnd)
		self.state = False

	def notify(self):
		with winclip.clipboard(self.hwnd):
			data = winclip.get_clipboard_data()
			if data and data.strip():
				if config.conf["autoclip"]["interrupt"]:
					speech.cancelSpeech()
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, (data))


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super().__init__()
		self.watcher = None
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(AutoclipSettings)
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.menuItem = self.toolsMenu.AppendCheckItem(wx.ID_ANY, _("&Automatic clipboard reading"), _("Toggles Automatic clipboard reading."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, lambda event: self.toggle(), self.menuItem)
		core.postNvdaStartup.register(self.onConfigInit)
		config.post_configProfileSwitch.register(self.onConfigInit)

	def onConfigInit(self):
		# called at NVDA startup if the add-on is configured to remember the state is enabled or disabled,
		#  as well as when a configuration profile is switched.
		if config.conf["autoclip"]["rememberState"] and not globalVars.appArgs.secure:
			value = config.conf["autoclip"]["automaticClipboardReading"]
			if value:
				if self.watcher and self.watcher.state:
					return  # already enabled
				self.enable()
			elif not value:
				if not self.watcher:
					return  # already disabled
				self.disable()

	@scriptHandler.script(
		description=_("Toggles Automatic clipboard reading."),
		gesture="kb:NVDA+control+shift+k",
	)
	def script_toggleAutoclip(self, gesture):
		self.toggle()

	def enable(self):
		if self.watcher:
			return
		self.watcher = ClipboardWatcher()
		self.watcher.start()
		log.debug("Enabled")
		self.menuItem.Check()

	def disable(self):
		if not self.watcher:
			return
		if self.watcher.state:
			self.watcher.stop()
		self.watcher = None
		log.debug("Disabled")
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

	def terminate(self):
		super().terminate()
		self.disable()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(AutoclipSettings)
		core.postNvdaStartup.unregister(self.onConfigInit)
		config.post_configProfileSwitch.unregister(self.onConfigInit)
		self.toolsMenu.Delete(self.menuItem)
		self.menuItem = None


confspec = {
	"interrupt": "boolean(default=false)",
	"rememberState": "boolean(default=false)",
	"automaticClipboardReading": "boolean(default=false)",
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
			wx.CheckBox(self, label=_("&Remember the state of automatic clipboard reading after  NVDA restart. This option must be enabled for use in configuration profiles"))
		)
		self.interruptCB.SetValue(config.conf["autoclip"]["interrupt"])
		self.rememberCB.SetValue(config.conf["autoclip"]["rememberState"])

	def onSave(self):
		config.conf["autoclip"]["interrupt"] = self.interruptCB.IsChecked()
		config.conf["autoclip"]["rememberState"] = self.rememberCB.IsChecked()
		plugin = [p for p in globalPluginHandler.runningPlugins if type(p) is GlobalPlugin][0]
		queueHandler.queueFunction(queueHandler.eventQueue, plugin.onConfigInit)
