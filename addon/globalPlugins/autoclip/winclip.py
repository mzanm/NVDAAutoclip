# winclip
# utilities of win32 to access the clipboard, register to get clipboard update notifications, Etc.
# A part of the Autoclip add-on for NVDA
# Copyright (C) 2023 Mazen Alharbi
# This file is covered by the GNU General Public License Version 2.
# See the file LICENSE for more details.
# If the LICENSE file is not available, you can find the  GNU General Public License Version 2 at this link:
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import contextlib
import ctypes
import sys
import time
from ctypes.wintypes import (
    ATOM,
    BOOL,
    DWORD,
    HANDLE,
    HBRUSH,
    HGLOBAL,
    HICON,
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

HCURSOR = HANDLE
LRESULT = ctypes.c_longlong if sys.maxsize > 2**32 else ctypes.c_long
CF_UNICODETEXT = 13
WM_CLIPBOARDUPDATE = 0x031D
GWL_WNDPROC = -4
HWND_MESSAGE = -3


WNDPROC = ctypes.WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)


class WNDCLASSEX(ctypes.Structure):
    _fields_ = (
        ("cbSize", UINT),
        ("style", UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", INT),
        ("cbWndExtra", INT),
        ("hInstance", HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HICON),
    )


def error_check(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            error_code = ctypes.GetLastError()

            if error_code != 0:
                error_message = f"Error in {func.__name__}"
                exc = ctypes.WinError(error_code)
                log.error(error_message, exc_info=exc)
        return result

    return wrapper


OpenClipboard = ctypes.windll.user32["OpenClipboard"]
OpenClipboard.argtypes = [HWND]
OpenClipboard.restype = BOOL

CloseClipboard = error_check(ctypes.windll.user32["CloseClipboard"])
CloseClipboard.argtypes = []
CloseClipboard.restype = BOOL

GetClipboardData = error_check(ctypes.windll.user32["GetClipboardData"])
GetClipboardData.argtypes = [UINT]
GetClipboardData.restype = HANDLE

AddClipboardFormatListener = error_check(ctypes.windll.user32["AddClipboardFormatListener"])
AddClipboardFormatListener.argtypes = [HWND]
AddClipboardFormatListener.restype = BOOL

RemoveClipboardFormatListener = error_check(ctypes.windll.user32["RemoveClipboardFormatListener"])
RemoveClipboardFormatListener.argtypes = [HWND]
RemoveClipboardFormatListener.restype = BOOL

GlobalLock = error_check(ctypes.windll.kernel32["GlobalLock"])
GlobalLock.argtypes = [HGLOBAL]
GlobalLock.restype = LPVOID

GlobalUnlock = error_check(ctypes.windll.kernel32["GlobalUnlock"])
GlobalUnlock.argtypes = [HGLOBAL]
GlobalUnlock.restype = BOOL

GetModuleHandle = error_check(ctypes.windll.kernel32["GetModuleHandleW"])
GetModuleHandle.argtypes = [LPCWSTR]
GetModuleHandle.restype = HMODULE

RegisterClassEx = error_check(ctypes.windll.user32["RegisterClassExW"])
RegisterClassEx.argtypes = [WNDCLASSEX]
RegisterClassEx.restype = ATOM

UnregisterClass = error_check(ctypes.windll.user32["UnregisterClassW"])
UnregisterClass.argtypes = [LPCWSTR, HINSTANCE]
UnregisterClass.restype = BOOL

CreateWindowEx = error_check(ctypes.windll.user32["CreateWindowExW"])
CreateWindowEx.argtypes = [
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
CreateWindowEx.restype = HWND

DestroyWindow = error_check(ctypes.windll.user32["DestroyWindow"])
DestroyWindow.argtypes = [HWND]
DestroyWindow.restype = BOOL

DefWindowProc = ctypes.windll.user32["DefWindowProcW"]
DefWindowProc.argtypes = [HWND, UINT, WPARAM, LPARAM]
DefWindowProc.restype = ctypes.c_long


@contextlib.contextmanager
def clipboard(hwnd):
    # a program could be opening the clipboard, so we'll try for at least a quarter of a second to open it
    t = time.monotonic() + 0.25
    while time.monotonic() < t:
        s = OpenClipboard(hwnd)
        if s:
            break
        if not s:
            log.warning("Error while trying to open clipboard.", exc_info=ctypes.WinError())
            time.sleep(0.01)
    try:
        yield
    finally:
        CloseClipboard()


def get_clipboard_data(data_format=CF_UNICODETEXT):
    handle = GetClipboardData(data_format)
    if not handle:
        log.warning("Could not get clipboard data", exc_info=ctypes.WinError())
        return ""
    locked_handle = GlobalLock(handle)
    try:
        data = ctypes.c_wchar_p(locked_handle).value
        return data if data else ""
    finally:
        GlobalUnlock(handle)


class ClipboardMessageWindow:
    def __init__(self):
        self.on_clipboard_update = None
        self._raw_wndproc = None

        @WNDPROC
        def _raw_wndproc(hwnd, msg, wparam, lparam):
            if msg == WM_CLIPBOARDUPDATE and self.on_clipboard_update:
                try:
                    self.on_clipboard_update()
                except Exception:
                    log.exception("Error in window proc notify")
                return 0
            return DefWindowProc(hwnd, msg, wparam, lparam)

        self._raw_wndproc = _raw_wndproc

        self._wndclass = WNDCLASSEX(
            cbSize=ctypes.sizeof(WNDCLASSEX),
            lpfnWndProc=_raw_wndproc,
            hInstance=GetModuleHandle(None),
            lpszClassName="clipboardWatcherAuto",
        )

        self._atom = RegisterClassEx(ctypes.byref(self._wndclass))
        self.hwnd = CreateWindowEx(
            0,
            self._atom,
            None,
            0,
            0,
            0,
            0,
            0,
            HWND_MESSAGE,
            None,
            GetModuleHandle(None),
            None,
        )
        AddClipboardFormatListener(self.hwnd)

    def destroy(self):
        RemoveClipboardFormatListener(self.hwnd)
        self.on_clipboard_update = None
        DestroyWindow(self.hwnd)
        UnregisterClass(self._atom, GetModuleHandle(None))
        self._wndclass = None
        self._raw_wndproc = None
