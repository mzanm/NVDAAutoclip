# winclip
# utilities of win32 to access the clipboard, regester to get clippboard update notifications, Etc.
# A part of the Autoclip add-on for NVDA
# Copyright (C) 2023 Mazen Alharbi
# This file is covered by the GNU General Public License Version 2.
# See the file LICENSE for more details.
# If the LICENSE file is not available, you can find the  GNU General Public License Version 2 at this link:
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import contextlib
import ctypes
import time
from ctypes.wintypes import (
	BOOL,
	DWORD,
	HANDLE,
	HGLOBAL,
	HINSTANCE,
	HMENU,
	HMODULE,
	HWND,
	INT,
	LPARAM,
	LPCWSTR,
	LPVOID,
	UINT,
	WPARAM,
)

from logHandler import log

CF_UNICODETEXT = 13
WM_CLIPBOARDUPDATE = 0x031D
GWL_WNDPROC = -4
HWND_MESSAGE = -3


class win32clip:
	def __init__(self):

		self.OpenClipboard = ctypes.windll.user32["OpenClipboard"]
		self.OpenClipboard.argtypes = [HWND]
		self.OpenClipboard.restype = BOOL

		self.CloseClipboard = error_check(ctypes.windll.user32["CloseClipboard"])
		self.CloseClipboard.argtypes = []
		self.CloseClipboard.restype = BOOL

		self.GetClipboardData = error_check(ctypes.windll.user32["GetClipboardData"])
		self.GetClipboardData.argtypes = [UINT]
		self.GetClipboardData.restype = HANDLE

		self.AddClipboardFormatListener = error_check(ctypes.windll.user32["AddClipboardFormatListener"])
		self.AddClipboardFormatListener.argtypes = [HWND]
		self.AddClipboardFormatListener.restype = BOOL

		self.RemoveClipboardFormatListener = error_check(ctypes.windll.user32["RemoveClipboardFormatListener"])
		self.RemoveClipboardFormatListener.argtypes = [HWND]
		self.RemoveClipboardFormatListener.restype = BOOL

		self.GlobalLock = error_check(ctypes.windll.kernel32["GlobalLock"])
		self.GlobalLock.argtypes = [HGLOBAL]
		self.GlobalLock.restype = LPVOID

		self.GlobalUnlock = error_check(ctypes.windll.kernel32["GlobalUnlock"])
		self.GlobalUnlock.argtypes = [HGLOBAL]
		self.GlobalUnlock.restype = BOOL

		self.GetModuleHandle = error_check(ctypes.windll.kernel32["GetModuleHandleW"])
		self.GetModuleHandle.argtypes = [LPCWSTR]
		self.GetModuleHandle.restype = HMODULE

		self.CreateWindow = error_check(ctypes.windll.user32["CreateWindowExW"])
		self.CreateWindow.argtypes = [
			DWORD,
			LPCWSTR,
			LPCWSTR,
			DWORD,
			INT,
			INT,
			INT,
			INT,
			HWND,
			HMENU,
			HINSTANCE,
			LPVOID,
		]
		self.CreateWindow.restype = HWND

		self.DestroyWindow = error_check(ctypes.windll.user32["DestroyWindow"])
		self.DestroyWindow.argtypes = [HWND]
		self.DestroyWindow.restype = BOOL

		self.SetWindowLong = error_check(ctypes.windll.user32["SetWindowLongW"])
		self.SetWindowLong.argtypes = [HWND, INT, ctypes.c_void_p]
		self.SetWindowLong.restype = ctypes.c_long

		self.DefWindowProc = ctypes.windll.user32["DefWindowProcW"]
		self.DefWindowProc.argtypes = [HWND, UINT, WPARAM, LPARAM]
		self.DefWindowProc.restype = ctypes.c_long

	@contextlib.contextmanager
	def clipboard(self, hwnd):
		# a program could be opening the clipboard, so we'll try for at least a quartor of a second to open it
		t = time.time() + 0.25
		while time.time() < t:
			s = self.OpenClipboard(hwnd)
			if not s:
				log.warning("Error while trying to open clipboard.", exc_info=ctypes.WinError())
			if s:
				break
			time.sleep(0.01)
		try:
			yield
		finally:
			self.CloseClipboard()

	def get_clipboard_data(self, format=CF_UNICODETEXT):
		handle = self.GetClipboardData(format)
		if not handle:
			log.warning("Could not get clipboard data", exc_info= ctypes.WinError())
			return ""
		locked_handle = self.GlobalLock(handle)
		try:
			data = ctypes.c_wchar_p(locked_handle).value
			return data if data else ""
		finally:
			self.GlobalUnlock(handle)


def error_check(func):
	def wrapper(*args, **kwargs):
		result = func(*args, **kwargs)
		if not result:
			error_code = ctypes.get_last_error()

			if error_code != 0:
				error_message = f"Error in {func.__name__}"
				exc = ctypes.WinError(error_code)
				log.error(error_message, exc_info= exc)
		return result

	return wrapper
