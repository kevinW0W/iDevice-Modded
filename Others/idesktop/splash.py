"""Show a branded startup splash while the iDesktop viewer is starting."""
from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import tkinter as tk
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageTk

from . import window_position

TITLE = "iDesktop"
SPLASH_WIDTH = 900
SPLASH_HEIGHT = 590
POSITION_FILE = Path(os.environ.get("APPDATA", Path.home())) / "iDesktop" / "splash-position.json"
_GWL_EXSTYLE = -20
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_APPWINDOW = 0x00040000
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_NOZORDER = 0x0004
_SWP_NOACTIVATE = 0x0010
_SWP_FRAMECHANGED = 0x0020
_SW_MINIMIZE = 6


def _is_viewer_title(title: str) -> bool:
    return title == TITLE or title.startswith(TITLE + " (")


def viewer_window_open() -> bool:
    user32 = ctypes.windll.user32
    found = False
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL

    @callback_type
    def visit(hwnd, _):
        nonlocal found
        if not user32.IsWindowVisible(hwnd):
            return True
        title = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, title, len(title))
        if _is_viewer_title(title.value):
            found = True
            return False
        return True

    user32.EnumWindows(visit, 0)
    return found


def _make_background(size: tuple[int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(height):
        blend = y / max(1, height - 1)
        color = tuple(round(top * (1 - blend) + bottom * blend)
                      for top, bottom in zip((6, 13, 30), (11, 25, 55)))
        for x in range(width):
            pixels[x, y] = color

    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((width * 0.38, -height * 0.7, width * 1.15, height * 0.8),
                 fill=(13, 95, 255, 95))
    draw.ellipse((-width * 0.45, height * 0.55, width * 0.6, height * 1.55),
                 fill=(92, 48, 225, 58))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    image = Image.alpha_composite(image.convert("RGBA"), glow)
    wave = Image.new("RGBA", size, (0, 0, 0, 0))
    wave_draw = ImageDraw.Draw(wave)
    for index, color in enumerate(((45, 122, 255, 25), (34, 86, 220, 22), (87, 67, 210, 18))):
        offset = index * 36
        wave_draw.arc((-240 + offset, -height, width + 210, height * 1.55),
                      205, 335, fill=color, width=32)
    image = Image.alpha_composite(image, wave.filter(ImageFilter.GaussianBlur(12)))
    return image.convert("RGB")


def _make_laptop_frame(screenshot: Image.Image, size: tuple[int, int] = (440, 300)) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    screen_left, screen_top = 18, 5
    screen_width, screen_height = width - 36, height - 48
    draw.rounded_rectangle(
        (screen_left, screen_top, screen_left + screen_width, screen_top + screen_height),
        radius=18,
        fill=(161, 171, 188, 255),
        outline=(214, 223, 236, 255),
        width=2,
    )
    inset = 7
    inner = (screen_left + inset, screen_top + inset,
             screen_left + screen_width - inset, screen_top + screen_height - inset)
    display_size = (inner[2] - inner[0], inner[3] - inner[1])
    display = ImageOps.fit(screenshot.convert("RGB"), display_size, method=Image.Resampling.LANCZOS)
    mask = Image.new("L", display_size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, display_size[0] - 1, display_size[1] - 1),
                                           radius=10, fill=255)
    image.paste(display, (inner[0], inner[1]), mask)
    draw = ImageDraw.Draw(image)
    notch_width = 42
    draw.rounded_rectangle((width // 2 - notch_width // 2, screen_top + 1,
                            width // 2 + notch_width // 2, screen_top + 8),
                           radius=4, fill=(19, 23, 31, 255))
    draw.ellipse((width // 2 - 2, screen_top + 3, width // 2 + 2, screen_top + 7),
                 fill=(52, 69, 92, 255))

    base_top = screen_top + screen_height - 1
    base_bottom = height - 24
    base_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    base_pixels = base_layer.load()
    for y in range(base_top, base_bottom + 1):
        blend = (y - base_top) / max(1, base_bottom - base_top)
        color = tuple(round(a * (1 - blend) + b * blend)
                      for a, b in zip((185, 194, 208), (103, 116, 137)))
        for x in range(width):
            base_pixels[x, y] = (*color, 255)
    image.alpha_composite(base_layer)
    draw = ImageDraw.Draw(image)
    draw.polygon(((2, base_bottom), (width - 2, base_bottom),
                  (width - 24, height - 7), (24, height - 7)),
                 fill=(134, 146, 165, 255))
    draw.line((24, height - 8, width - 24, height - 8), fill=(214, 221, 231, 210), width=1)
    draw.rounded_rectangle((width // 2 - 48, base_top + 7, width // 2 + 48, base_top + 11),
                           radius=2, fill=(77, 88, 106, 190))
    draw.ellipse((width // 2 - 3, height - 7, width // 2 + 3, height - 4),
                 fill=(79, 91, 109, 220))
    return image


def _draw_pill(canvas: tk.Canvas, x0: float, y0: float, x1: float, y1: float, color: str) -> None:
    radius = (y1 - y0) / 2
    canvas.create_rectangle(x0 + radius, y0, x1 - radius, y1, fill=color, outline="")
    canvas.create_oval(x0, y0, x0 + 2 * radius, y1, fill=color, outline="")
    canvas.create_oval(x1 - 2 * radius, y0, x1, y1, fill=color, outline="")


def _center_position(screen_width: int, screen_height: int) -> tuple[int, int]:
    return (screen_width - SPLASH_WIDTH) // 2, (screen_height - SPLASH_HEIGHT) // 2


def _monitor_work_areas() -> list[tuple[int, int, int, int]]:
    return window_position.monitor_work_areas()


def _clamp_position(
    x: int,
    y: int,
    work_areas: list[tuple[int, int, int, int]],
    width: int = SPLASH_WIDTH,
    height: int = SPLASH_HEIGHT,
) -> tuple[int, int]:
    return window_position.clamp_position(x, y, work_areas, width, height)


def _load_position() -> tuple[int, int] | None:
    return window_position.load_position(POSITION_FILE)


def _save_position(x: int, y: int) -> None:
    window_position.save_position(POSITION_FILE, x, y)


def _taskbar_extended_style(style: int) -> int:
    return (style | _WS_EX_APPWINDOW) & ~_WS_EX_TOOLWINDOW


def _toplevel_hwnd(root: tk.Tk) -> int:
    return int(root.tk.call("wm", "frame", root._w), 0)


def _enable_taskbar_button(root: tk.Tk) -> None:
    if os.name != "nt":
        return
    root.update_idletasks()
    user32 = ctypes.windll.user32
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL
    hwnd = _toplevel_hwnd(root)
    style = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
    ctypes.set_last_error(0)
    user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, _taskbar_extended_style(style))
    error = ctypes.get_last_error()
    if error:
        raise ctypes.WinError(error)
    flags = _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOZORDER | _SWP_NOACTIVATE | _SWP_FRAMECHANGED
    if not user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, flags):
        raise ctypes.WinError()


def _minimize_splash(root: tk.Tk) -> None:
    if os.name == "nt":
        ctypes.windll.user32.ShowWindow(_toplevel_hwnd(root), _SW_MINIMIZE)
    else:
        root.iconify()


def main() -> None:
    root = tk.Tk()
    root.title(TITLE + " startup")
    root.overrideredirect(True)
    if os.name == "nt":
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "idesktop.ico"
        root.iconbitmap(str(icon_path))
    root.configure(bg="#080f21")
    root.resizable(False, False)
    root.withdraw()
    root.update_idletasks()
    position = _load_position()
    if position is not None:
        x, y = position
    work_areas = _monitor_work_areas() if os.name == "nt" else []
    if not work_areas:
        work_areas = [(0, 0, root.winfo_screenwidth(), root.winfo_screenheight())]
    if position is None:
        primary = work_areas[0]
        x, y = _center_position(primary[2] - primary[0], primary[3] - primary[1])
        x += primary[0]
        y += primary[1]
    x, y = _clamp_position(x, y, work_areas)
    root.geometry(f"{SPLASH_WIDTH}x{SPLASH_HEIGHT}+{x}+{y}")
    root.deiconify()
    root.update_idletasks()
    _enable_taskbar_button(root)

    panel_x, panel_y, panel_width, panel_height = 54, 35, 792, 520
    canvas = tk.Canvas(root, width=SPLASH_WIDTH, height=SPLASH_HEIGHT,
                       bg="#080f21", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    background = ImageTk.PhotoImage(_make_background((SPLASH_WIDTH, SPLASH_HEIGHT)))
    canvas.create_image(0, 0, image=background, anchor="nw")
    canvas.background = background
    canvas.create_rectangle(panel_x, panel_y, panel_x + panel_width, panel_y + panel_height,
                            fill="#171e2b", outline="#344158", width=1)

    panel = tk.Frame(root, bg="#171e2b", highlightthickness=0)
    canvas.create_window(panel_x + 1, panel_y + 1, anchor="nw",
                         width=panel_width - 2, height=panel_height - 2, window=panel)

    header = tk.Frame(panel, bg="#171e2b")
    header.place(x=24, y=16, width=panel_width - 48, height=38)
    header_title = tk.Label(header, text="iDevice Modded", font=("Segoe UI", 10, "bold"),
                            fg="#dce8ff", bg="#171e2b", cursor="fleur")
    header_title.pack(side="left")
    minimize_button = tk.Button(
        header, text="−", command=lambda: _minimize_splash(root), borderwidth=0,
        font=("Segoe UI", 15), fg="#b8c5db", bg="#171e2b",
        activebackground="#293449", activeforeground="white",
        cursor="hand2", relief="flat",
    )
    minimize_button.pack(side="right", padx=(0, 7))
    close_button = tk.Button(
        header, text="×", command=root.destroy, borderwidth=0,
        font=("Segoe UI", 16), fg="#b8c5db", bg="#171e2b",
        activebackground="#293449", activeforeground="white",
        cursor="hand2", relief="flat",
    )
    close_button.pack(side="right", padx=(0, 3))

    drag_origin = (0, 0, 0, 0)
    last_position = (x, y)

    def begin_drag(event: tk.Event) -> None:
        nonlocal drag_origin
        drag_origin = (event.x_root, event.y_root, root.winfo_x(), root.winfo_y())

    def move_splash(event: tk.Event) -> None:
        nonlocal last_position
        pointer_x, pointer_y, window_x, window_y = drag_origin
        x = window_x + event.x_root - pointer_x
        y = window_y + event.y_root - pointer_y
        last_position = (x, y)
        root.geometry(f"+{x}+{y}")

    save_job = None

    def schedule_save(_event: tk.Event | None = None) -> None:
        nonlocal last_position, save_job
        if root.state() != "normal":
            return
        last_position = (root.winfo_x(), root.winfo_y())
        if save_job is not None:
            root.after_cancel(save_job)
        save_job = root.after(300, lambda: _save_position(*last_position))

    def save_on_destroy(event: tk.Event) -> None:
        nonlocal save_job
        if event.widget is root:
            if save_job is not None:
                root.after_cancel(save_job)
            _save_position(*last_position)

    root.bind("<Configure>", schedule_save)
    root.bind("<Destroy>", save_on_destroy)

    for drag_widget in (header, header_title):
        drag_widget.bind("<ButtonPress-1>", begin_drag)
        drag_widget.bind("<B1-Motion>", move_splash)

    title = tk.Label(panel, text="Getting iDesktop ready", font=("Segoe UI", 21, "bold"),
                     fg="#f5f7fc", bg="#171e2b")
    title.place(x=28, y=70)
    subtitle = tk.Label(panel, text="Starting your iPhone desktop experience",
                        font=("Segoe UI", 10), fg="#abb8ce", bg="#171e2b")
    subtitle.place(x=30, y=111)

    project_root = Path(__file__).resolve().parents[1]
    preview_path = project_root / "assets" / "idesktop-install-preview.png"
    try:
        screenshot = Image.open(preview_path)
        laptop = ImageTk.PhotoImage(_make_laptop_frame(screenshot))
        device_preview = tk.Label(panel, image=laptop, bg="#171e2b", borderwidth=0)
        device_preview.image = laptop
        device_preview.place(x=18, y=145)
    except (OSError, ValueError):
        device_preview = tk.Label(
            panel, text="iDesktop", font=("Segoe UI", 24, "bold"),
            fg="#8cb7ff", bg="#101a2b", width=32, height=9,
        )
        device_preview.place(x=30, y=165)

    status_title = tk.Label(panel, text="Connecting to your iPhone",
                            font=("Segoe UI", 12, "bold"), fg="#edf2fc", bg="#171e2b",
                            wraplength=250, justify="left")
    status_title.place(x=480, y=158)
    status_copy = tk.Label(
        panel,
        text="iDesktop is starting its services and preparing the live desktop view.",
        font=("Segoe UI", 9), fg="#aab7ca", bg="#171e2b",
        wraplength=245, justify="left",
    )
    status_copy.place(x=480, y=188)

    tk.Label(panel, text="STARTUP LOG", font=("Segoe UI", 8, "bold"),
             fg="#8da8d0", bg="#171e2b").place(x=480, y=252)
    log_panel = tk.Text(panel, height=8, width=34, state="disabled", wrap="word",
                        background="#101723", foreground="#bac8dc",
                        insertbackground="#bac8dc", borderwidth=0, padx=10, pady=8,
                        font=("Consolas", 8), highlightthickness=1,
                        highlightbackground="#2d3a50")
    log_panel.place(x=480, y=274, width=270, height=136)

    log_path = (Path(os.environ.get("APPDATA", Path.home())) / "iDesktop" / "logs" / "launcher.log")
    initial_log = "Waiting for iDesktop startup..."

    def refresh_log() -> None:
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-7:]
            content = "\n".join(line[-180:] for line in lines) or initial_log
        except OSError:
            content = initial_log
        log_panel.configure(state="normal")
        log_panel.delete("1.0", "end")
        log_panel.insert("1.0", content)
        log_panel.see("end")
        log_panel.configure(state="disabled")

    refresh_log()

    progress_label = tk.Label(panel, text="INITIALIZING", font=("Segoe UI", 8, "bold"),
                              fg="#8da8d0", bg="#171e2b")
    progress_label.place(x=28, y=437)
    hint = tk.Label(panel, text="This window will close when iDesktop is ready",
                    font=("Segoe UI", 8), fg="#98a6bb", bg="#171e2b")
    hint.place(x=410, y=437)
    progress = tk.Canvas(panel, height=12, bg="#171e2b", highlightthickness=0)
    progress.place(x=28, y=462, width=panel_width - 56, height=12)

    offset = 0.0
    startup_stopped = False

    def animate_progress() -> None:
        nonlocal offset
        if startup_stopped:
            return
        progress.delete("all")
        width = progress.winfo_width()
        height = progress.winfo_height()
        if width <= 1:
            root.after(40, animate_progress)
            return
        _draw_pill(progress, 0, 2, width, height - 2, "#293449")
        segment_width = max(72, width * 0.22)
        left = offset - segment_width
        _draw_pill(progress, left, 2, left + segment_width, height - 2, "#63a5ff")
        offset = (offset + max(3, width / 100)) % (width + segment_width)
        root.after(32, animate_progress)

    try:
        no_window = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        app = subprocess.Popen([sys.executable, "-m", "idesktop", *sys.argv[1:]],
                               cwd=project_root, creationflags=no_window)
    except OSError as exc:
        app = None
        startup_stopped = True
        title.configure(text="iDesktop could not start")
        subtitle.configure(text=str(exc))
        progress_label.configure(text="STARTUP FAILED", fg="#ff9a9a")
        hint.configure(text="Close this window and check your installation")

    def check_startup() -> None:
        nonlocal startup_stopped
        refresh_log()
        if viewer_window_open():
            root.destroy()
        elif app is not None and app.poll() is not None and not startup_stopped:
            startup_stopped = True
            title.configure(text="iDesktop stopped during startup")
            subtitle.configure(text="Check the startup log above for details.")
            progress_label.configure(text="STARTUP STOPPED", fg="#ff9a9a")
            hint.configure(text="Close this window after reviewing the log")
        else:
            root.after(350, check_startup)

    root.bind("<Escape>", lambda _event: root.destroy())
    if not startup_stopped:
        root.after(0, animate_progress)
        root.after(250, check_startup)
    root.mainloop()


if __name__ == "__main__":
    main()
