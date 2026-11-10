import ctypes
from ctypes import wintypes

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105
VK_CONTROL = {0x11, 0xA2, 0xA3}
VK_ALT = {0x12, 0xA4, 0xA5}
VK_SHIFT = {0x10, 0xA0, 0xA1}
VK_WIN = {0x5B, 0x5C}
VIEWER_TITLES = {"iDesktop", "iDesktop (Lite mode)"}

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HMODULE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p]
user32.CallNextHookEx.restype = ctypes.c_int
user32.GetMessageW.argtypes = [ctypes.POINTER(ctypes.wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = ctypes.c_int
user32.TranslateMessage.argtypes = [ctypes.POINTER(ctypes.wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(ctypes.wintypes.MSG)]
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
pressed = set()
locked = True


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


def viewer_is_foreground() -> bool:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    title = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, title, len(title))
    return title.value in VIEWER_TITLES


def _toggle_if_host_chord(vk: int) -> bool:
    global locked
    first_press = vk not in pressed
    pressed.add(vk)
    has_control = bool(pressed & VK_CONTROL)
    has_alt = bool(pressed & VK_ALT)
    has_shift = bool(pressed & VK_SHIFT)
    has_win = bool(pressed & VK_WIN)
    if first_press and has_control and has_alt and has_shift and has_win:
        locked = not locked
        return True
    return False


@HOOKPROC
def hook(code: int, message: int, lparam: int) -> int:
    if code < 0:
        return user32.CallNextHookEx(None, code, message, lparam)
    if not viewer_is_foreground():
        pressed.clear()
        return user32.CallNextHookEx(None, code, message, lparam)
    if message in (WM_KEYDOWN, WM_SYSKEYDOWN):
        info = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk = info.vkCode
        if _toggle_if_host_chord(vk):
            return 1
        if locked and (vk in VK_WIN or bool(pressed & VK_WIN)):
            return 1
    elif message in (WM_KEYUP, WM_SYSKEYUP):
        info = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        pressed.discard(info.vkCode)
    return user32.CallNextHookEx(None, code, message, lparam)

def main() -> None:
    handle = user32.SetWindowsHookExW(WH_KEYBOARD_LL, hook, None, 0)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    message = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))
    finally:
        user32.UnhookWindowsHookEx(handle)


if __name__ == "__main__":
    main()
