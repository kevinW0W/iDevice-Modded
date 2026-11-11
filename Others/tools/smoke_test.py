"""Exercise code paths that only run with a phone / viewer window, as far as possible without
either: catches missing names and broken wiring that compiling alone doesn't (no phone needed).
Usage: python tools/smoke_test.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

failures = []


def check(name, fn):
    try:
        fn()
        print("PASS", name)
    except Exception as e:  # noqa: BLE001 - report everything
        failures.append(name)
        print("FAIL", name, f"{type(e).__name__}: {e}")


def winshape_without_window():
    from idesktop import winshape
    winshape._hwnd = None
    winshape.TITLE = "iDesktop smoke test (no such window)"
    assert winshape.find_window() is None
    for spec in ({"dpr": 1, "maximize": True, "shapes": [{"x": 0, "y": 0, "w": 10, "h": 10, "r": 2}]},
                 {"off": True}):
        try:
            winshape.apply_layout(spec)
        except RuntimeError as e:
            assert "not found" in str(e)
        else:
            raise AssertionError("expected 'viewer window not found'")
    winshape.move_by(1, 1)      # no window: quietly nothing
    winshape.command("min")


def winshape_minimized_layout_is_deferred():
    from unittest.mock import patch

    from idesktop import winshape
    with patch.object(winshape, "find_window", return_value=1), \
            patch.object(winshape.user32, "IsIconic", return_value=True):
        result = winshape._apply({"dpr": 1, "maximize": True, "shapes": []})
    assert result == {"ok": True, "deferred": True}


def native_patches_apply():
    from pymobiledevice3.remote.core_device import screen_stream as ss

    from idesktop import native
    native.patch_screen_stream(18091, "com.example.wda", 18100)
    native.patch_wifi_fallback("192.0.2.1")
    native.patch_userspace_dial_timeout()
    from pymobiledevice3.remote import userspace_tunnel as ut
    assert ut.UserspaceTun.connect_tcp.__module__ == "idesktop.native"
    assert hasattr(ut, "pytcp_socket") and hasattr(ut, "AF_INET6") and hasattr(ut, "SOCK_STREAM")
    from pmd_net_addr import Ip6Address
    from pmd_pytcp.socket import tcp__socket
    ports = {tcp__socket.pick_local_port_for(local_ip=Ip6Address("fd00::2"), remote_ip=Ip6Address("fd00::1"),
                                             remote_port=8100) for _ in range(6)}
    assert len(ports) > 1, "source ports must not repeat per destination"
    assert "keyboard" in ss._NAMED_BUTTONS
    html = native.build_html(ss.VIEWER_HTML if isinstance(ss.VIEWER_HTML, bytes) else ss.VIEWER_HTML.encode(), 18091)
    assert b"<title>iDesktop</title>" in html and b"127.0.0.1:18091" in html


def audio_decoder_opens():
    from idesktop.native import FFmpegAACELDDecoder
    d = FFmpegAACELDDecoder()
    assert d.decode(b"\x00\x00") == FFmpegAACELDDecoder.SILENCE


def helpers_import():
    from idesktop import app, controller, device, wda
    assert device.CONFIG_DIR.name == "iDesktop"
    assert callable(controller.main) and hasattr(wda, "WDA")
    assert app._centered_window_bounds((0, 0, 1920, 1080)) == (468, 900, 726, 90)
    assert app._centered_window_bounds((0, 0, 2880, 1620), scale=1.5) == (468, 900, 726, 90)
    assert app._centered_window_bounds((100, 50, 2020, 1130)) == (468, 900, 826, 140)
    native = __import__("idesktop.native", fromlist=["x"])
    assert (app.RECONNECT_EXIT, app.DISCONNECT_EXIT, app.RECONNECT_FLAG) ==         (native.RECONNECT_EXIT, native.DISCONNECT_EXIT, native.RECONNECT_FLAG)


def root_launcher_wiring():
    repo = ROOT.parent
    launcher = (repo / "iDesktop.bat").read_text(encoding="utf-8")
    hidden_launcher = (repo / "iDesktop.vbs").read_text(encoding="utf-8")
    nested_launcher = (ROOT / "iDesktop.bat").read_text(encoding="utf-8")
    installer = (ROOT / "installer" / "idesktop.iss").read_text(encoding="utf-8")
    powershell_installer = (ROOT / "install.ps1").read_text(encoding="utf-8")

    assert "set \"IDESKTOP_CODE_HOME=%IDESKTOP_HOME%Others\"" in launcher
    assert "-m idesktop.splash %*" in launcher
    assert 'shell.Run """" & launcher & """", 0, False' in hidden_launcher
    assert 'call "%~dp0..\\iDesktop.bat" %*' in nested_launcher
    assert 'Source: "{#ProjectRoot}\\..\\iDesktop.bat"; DestDir: "{app}"' in installer
    assert 'Source: "{#ProjectRoot}\\..\\iDesktop.vbs"; DestDir: "{app}"' in installer
    assert 'Filename: "{sys}\\wscript.exe"; Parameters: """{app}\\iDesktop.vbs"""' in installer
    assert "$launcher = Join-Path $src '..\\iDesktop.bat'" in powershell_installer
    assert "$s.TargetPath = Join-Path $env:WINDIR 'System32\\wscript.exe'" in powershell_installer
    assert "$s.Arguments = '\"' + (Join-Path $App 'iDesktop.vbs') + '\"'" in powershell_installer


def installer_uses_fork_branding():
    installer = (ROOT / "installer" / "idesktop.iss").read_text(encoding="utf-8")
    builder = (ROOT / "tools" / "build_installer.py").read_text(encoding="utf-8")
    assert '#define AppName "iDevice Modded"' in installer
    assert "VersionInfoProductName=iDevice Modded" in installer
    assert '"iDevice-Modded-Setup-" + AppVersion + "-x64"' in installer
    assert 'f"iDevice-Modded-Setup-{version}-x64.exe"' in builder


def splash_art_renders():
    from PIL import Image

    from idesktop.splash import _center_position, _draw_pill, _make_laptop_frame

    assert _center_position(1920, 1080) == (510, 245)
    splash_source = (ROOT / "idesktop" / "splash.py").read_text(encoding="utf-8")
    assert 'drag_widget.bind("<B1-Motion>", move_splash)' in splash_source
    assert "creationflags=no_window" in splash_source
    preview = Path(__file__).resolve().parents[1] / "assets" / "idesktop-install-preview.png"
    laptop = _make_laptop_frame(Image.open(preview))
    assert laptop.size == (440, 300) and laptop.getbbox() is not None

    class Canvas:
        def __init__(self):
            self.shapes = []

        def create_rectangle(self, *args, **kwargs):
            self.shapes.append(("rectangle", args, kwargs))

        def create_oval(self, *args, **kwargs):
            self.shapes.append(("oval", args, kwargs))

    canvas = Canvas()
    _draw_pill(canvas, 0, 0, 100, 10, "#63a5ff")
    assert [shape[0] for shape in canvas.shapes] == ["rectangle", "oval", "oval"]


check("winshape without a window", winshape_without_window)
check("minimized window layout is deferred", winshape_minimized_layout_is_deferred)
check("native patches apply", native_patches_apply)
check("audio decoder opens", audio_decoder_opens)
check("modules import", helpers_import)
check("root launcher targets and installed shortcuts", root_launcher_wiring)
check("installer uses fork branding", installer_uses_fork_branding)
check("splash artwork and rounded progress render", splash_art_renders)
sys.exit(1 if failures else 0)
