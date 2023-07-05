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

OpenClipboard = ctypes.windll.user32.OpenClipboard
OpenClipboard.argtypes = [HWND]
OpenClipboard.restype = BOOL

CloseClipboard = ctypes.windll.user32.CloseClipboard
CloseClipboard.argtypes = []
CloseClipboard.restype = BOOL

GetClipboardData = ctypes.windll.user32.GetClipboardData
GetClipboardData.argtypes = [UINT]
GetClipboardData.restype = HANDLE

AddClipboardFormatListener = ctypes.windll.user32.AddClipboardFormatListener
AddClipboardFormatListener.argtypes = [HWND]
AddClipboardFormatListener.restype = BOOL

RemoveClipboardFormatListener = ctypes.windll.user32.RemoveClipboardFormatListener
RemoveClipboardFormatListener.argtypes = [HWND]
RemoveClipboardFormatListener.restype = BOOL

GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalLock.argtypes = [HGLOBAL]
GlobalLock.restype = LPVOID

GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = [HGLOBAL]
GlobalUnlock.restype = BOOL

CreateWindow = ctypes.windll.user32.CreateWindowExW
CreateWindow.argtypes = [
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
CreateWindow.restype = HWND

DestroyWindow = ctypes.windll.user32.DestroyWindow
DestroyWindow.argtypes = [HWND]
DestroyWindow.restype = BOOL

SetWindowLong = ctypes.windll.user32.SetWindowLongW
SetWindowLong.argtypes = [HWND, INT, ctypes.c_void_p]
SetWindowLong.restype = ctypes.c_long

DefWindowProc = ctypes.windll.user32.DefWindowProcW
DefWindowProc.argtypes = [HWND, UINT, WPARAM, LPARAM]
DefWindowProc.restype = ctypes.c_long


@contextlib.contextmanager
def clipboard(hwnd):
	t = time.perf_counter() + 1
	while time.perf_counter() < t:
		s = OpenClipboard(hwnd)
		if not s:
			log.warning("Error while trying to open clipboard.", exc_info=ctypes.WinError())
		if s:
			break
		time.sleep(0.01)
	try:
		yield
	finally:
		CloseClipboard()


def get_clipboard_data(format=CF_UNICODETEXT):
	handle = GetClipboardData(format)
	if not handle:
		return ""
	locked_handle = GlobalLock(handle)
	if not locked_handle:
		log.warning("unable to lock clipboard handle")
		raise ctypes.WinError()
	try:
		data = ctypes.c_wchar_p(locked_handle).value
		return data if data else ""
	finally:
		GlobalUnlock(handle)
