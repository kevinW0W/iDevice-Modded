"""Persistence and display-aware recovery for top-level window positions."""
from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


class _MonitorInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def monitor_work_areas() -> list[tuple[int, int, int, int]]:
    user32 = ctypes.windll.user32
    primary = []
    secondary = []
    callback_type = ctypes.WINFUNCTYPE(
        wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM
    )

    @callback_type
    def visit(monitor, _dc, _rect, _data):
        info = _MonitorInfo()
        info.cbSize = ctypes.sizeof(info)
        if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            return False
        work = info.rcWork
        area = (work.left, work.top, work.right, work.bottom)
        (primary if info.dwFlags & 1 else secondary).append(area)
        return True

    user32.EnumDisplayMonitors.argtypes = [
        wintypes.HDC, ctypes.POINTER(wintypes.RECT), callback_type, wintypes.LPARAM
    ]
    user32.EnumDisplayMonitors.restype = wintypes.BOOL
    user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.POINTER(_MonitorInfo)]
    user32.GetMonitorInfoW.restype = wintypes.BOOL
    if not user32.EnumDisplayMonitors(None, None, visit, 0):
        raise ctypes.WinError()
    return primary + secondary


def clamp_position(
    x: int,
    y: int,
    work_areas: list[tuple[int, int, int, int]],
    width: int,
    height: int,
) -> tuple[int, int]:
    if not work_areas:
        raise ValueError("At least one monitor work area is required")

    def distance(area: tuple[int, int, int, int]) -> int:
        left, top, right, bottom = area
        dx = max(left - (x + width), 0, x - right)
        dy = max(top - (y + height), 0, y - bottom)
        return dx * dx + dy * dy

    left, top, right, bottom = min(work_areas, key=distance)
    max_x = max(left, right - width)
    max_y = max(top, bottom - height)
    return min(max(x, left), max_x), min(max(y, top), max_y)


def load_position(path: Path) -> tuple[int, int] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if (not isinstance(data, dict) or type(data.get("x")) is not int or
            type(data.get("y")) is not int):
        raise ValueError(f"Invalid window position in {path}")
    return data["x"], data["y"]


def save_position(path: Path, x: int, y: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps({"x": x, "y": y}), encoding="utf-8")
    os.replace(temp, path)
