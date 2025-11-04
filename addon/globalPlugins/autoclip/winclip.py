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
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

CF_UNICODETEXT = 13
WM_CLIPBOARDUPDATE = 0x031D

# prototypes
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL

user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL

user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
user32.IsClipboardFormatAvailable.restype = wintypes.BOOL

user32.GetClipboardData.argtypes = [wintypes.UINT]
user32.GetClipboardData.restype = wintypes.HANDLE  # HGLOBAL

kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = wintypes.LPVOID

kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL

kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]
SIZE_T = getattr(wintypes, "SIZE_T", ctypes.c_size_t)

kernel32.GlobalSize.restype = SIZE_T
from logHandler import log

HCURSOR = HANDLE
LRESULT = ctypes.c_longlong if sys.maxsize > 2**32 else ctypes.c_long
CF_UNICODETEXT = 13
WM_CLIPBOARDUPDATE = 0x031D
GWL_WNDPROC = -4
def _HWND_MESSAGE() -> HWND:
    """Return the special message-only window parent handle as an unsigned pointer."""
    ptr_bits = ctypes.sizeof(ctypes.c_void_p) * 8
    # -3 as an unsigned pointer (HWND is a pointer type; ctypes uses c_void_p)
    unsigned = (2 ** ptr_bits) - 3
    return ctypes.c_void_p(unsigned)  # acceptable where HWND is expected

# Optional: simple helpers for styles (not strictly needed)
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_POPUP = 0x80000000

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


def get_clipboard_data():

       hglob = user32.GetClipboardData(CF_UNICODETEXT)

       ptr = kernel32.GlobalLock(hglob)
       if not ptr:
             return None

       try:
            # Size is in BYTES for the global block (UTF-16: 2 bytes per wchar)
            size_bytes = kernel32.GlobalSize(hglob) or 0
            if size_bytes:
                max_wchars = size_bytes // ctypes.sizeof(ctypes.c_wchar)
                # Read at most that many wchar_t; strip trailing NULs
                text = ctypes.wstring_at(ptr, max_wchars).rstrip("\x00")
            else:
                # Fallback: rely on NUL termination if size is unavailable
                text = ctypes.wstring_at(ptr).rstrip("\x00")
            return text
       finally:
            kernel32.GlobalUnlock(hglob)

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
            _HWND_MESSAGE(),
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
 