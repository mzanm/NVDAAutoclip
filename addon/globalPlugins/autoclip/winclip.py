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

		self.OpenClipboard = copy_func(ctypes.windll.user32.OpenClipboard)
		self.OpenClipboard.argtypes = [HWND]
		self.OpenClipboard.restype = BOOL

		self.CloseClipboard = copy_func(ctypes.windll.user32.CloseClipboard)
		self.CloseClipboard.argtypes = []
		self.CloseClipboard.restype = BOOL

		self.GetClipboardData = copy_func(ctypes.windll.user32.GetClipboardData)
		self.GetClipboardData.argtypes = [UINT]
		self.GetClipboardData.restype = HANDLE

		self.AddClipboardFormatListener = copy_func(ctypes.windll.user32.AddClipboardFormatListener)
		self.AddClipboardFormatListener.argtypes = [HWND]
		self.AddClipboardFormatListener.restype = BOOL

		self.RemoveClipboardFormatListener = copy_func(ctypes.windll.user32.RemoveClipboardFormatListener)
		self.RemoveClipboardFormatListener.argtypes = [HWND]
		self.RemoveClipboardFormatListener.restype = BOOL

		self.GlobalLock = copy_func(ctypes.windll.kernel32.GlobalLock)
		self.GlobalLock.argtypes = [HGLOBAL]
		self.GlobalLock.restype = LPVOID

		self.GlobalUnlock = copy_func(ctypes.windll.kernel32.GlobalUnlock)
		self.GlobalUnlock.argtypes = [HGLOBAL]
		self.GlobalUnlock.restype = BOOL

		self.GetModuleHandle = copy_func(ctypes.windll.kernel32.GetModuleHandleW)
		self.GetModuleHandle.argtypes = [LPCWSTR]
		self.GetModuleHandle.restype = HMODULE

		self.CreateWindow = copy_func(ctypes.windll.user32.CreateWindowExW)
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

		self.DestroyWindow = copy_func(ctypes.windll.user32.DestroyWindow)
		self.DestroyWindow.argtypes = [HWND]
		self.DestroyWindow.restype = BOOL

		self.SetWindowLong = copy_func(ctypes.windll.user32.SetWindowLongW)
		self.SetWindowLong.argtypes = [HWND, INT, ctypes.c_void_p]
		self.SetWindowLong.restype = ctypes.c_long

		self.DefWindowProc = copy_func(ctypes.windll.user32.DefWindowProcW)
		self.DefWindowProc.argtypes = [HWND, UINT, WPARAM, LPARAM]
		self.DefWindowProc.restype = ctypes.c_long

	@contextlib.contextmanager
	def clipboard(self, hwnd):
		# a program could be opening the clipboard, so we'll try for at least half a second to open it
		t = time.perf_counter() + 0.5
		while time.perf_counter() < t:
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
			return ""
		locked_handle = self.GlobalLock(handle)
		if not locked_handle:
			log.error("unable to lock clipboard handle")
			raise ctypes.WinError()
		try:
			data = ctypes.c_wchar_p(locked_handle).value
			return data if data else ""
		finally:
			self.GlobalUnlock(handle)


def copy_func(func):
	# copy a ctypes func_ptr object
		func_type = type(func)
		coppied_func = func_type.from_address(ctypes.addressof(func))
		return coppied_func
