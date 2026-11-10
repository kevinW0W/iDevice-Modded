"""Build a self-contained, x64 Windows installer using Inno Setup."""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PYTHON_VERSION = "3.13.17"
PYTHON_URL = (
    f"https://www.python.org/ftp/python/{PYTHON_VERSION}/"
    f"python-{PYTHON_VERSION}-amd64.exe"
)
PYTHON_SHA256 = "5da012101ba2e17113a9a1cd901e9ce1441086f2b7ecb5de06ec94163899a190"


def download_python_installer(destination: Path) -> None:
    if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() == PYTHON_SHA256:
        return
    temporary = destination.with_suffix(".download")
    digest = hashlib.sha256()
    try:
        with urllib.request.urlopen(PYTHON_URL, timeout=60) as response, temporary.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                out.write(chunk)
        if digest.hexdigest() != PYTHON_SHA256:
            raise RuntimeError("The downloaded Python installer failed its SHA-256 check.")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def build_wheelhouse(build_dir: Path) -> Path:
    wheel_dir = build_dir / "wheelhouse"
    wheel_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--disable-pip-version-check",
            "--wheel-dir",
            str(wheel_dir),
            "-r",
            str(ROOT / "requirements.txt"),
        ],
        cwd=ROOT,
        check=True,
    )
    validation = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--dry-run",
            "--ignore-installed",
            "--no-index",
            "--find-links",
            str(wheel_dir),
            "-r",
            str(ROOT / "requirements.txt"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if validation.returncode:
        sys.stderr.write(validation.stdout)
        sys.stderr.write(validation.stderr)
        raise subprocess.CalledProcessError(validation.returncode, validation.args)
    archive_path = build_dir / "wheelhouse.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for wheel in sorted(wheel_dir.iterdir()):
            if wheel.is_file() and wheel.suffix == ".whl":
                archive.write(wheel, wheel.name)
    shutil.rmtree(wheel_dir)
    return archive_path


def make_wizard_art(build_dir: Path) -> Path:
    build_dir.mkdir(parents=True, exist_ok=True)
    width, height = 164, 314
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        blend = y / max(1, height - 1)
        top = (19, 19, 39)
        bottom = (43, 30, 73)
        color = tuple(round(top[i] * (1 - blend) + bottom[i] * blend) for i in range(3))
        for x in range(width):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((91, 12, 208, 128), fill=(89, 84, 199, 34))
    draw.ellipse((-87, 190, 81, 360), fill=(125, 86, 216, 26))
    draw.rounded_rectangle((14, 17, 150, 21), radius=2, fill=(133, 111, 250, 225))

    icon = Image.open(ROOT / "assets" / "idesktop.png").convert("RGBA")
    icon.thumbnail((68, 68), Image.Resampling.LANCZOS)
    image.alpha_composite(icon, ((width - icon.width) // 2, 73)) if image.mode == "RGBA" else image.paste(
        icon, ((width - icon.width) // 2, 73), icon
    )

    font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    bold_path = font_dir / "segoeuib.ttf"
    regular_path = font_dir / "segoeui.ttf"
    bold = ImageFont.truetype(str(bold_path), 18) if bold_path.exists() else ImageFont.load_default()
    regular = ImageFont.truetype(str(regular_path), 10) if regular_path.exists() else ImageFont.load_default()
    draw = ImageDraw.Draw(image, "RGBA")
    title = "iDesktop"
    box = draw.textbbox((0, 0), title, font=bold)
    draw.text(((width - box[2]) / 2, 158), title, font=bold, fill=(248, 246, 255, 255))
    lines = ("YOUR IPHONE", "ON YOUR DESKTOP", "HD  •  TOUCH  •  SOUND")
    for index, line in enumerate(lines):
        box = draw.textbbox((0, 0), line, font=regular)
        draw.text(((width - box[2]) / 2, 191 + index * 19), line, font=regular,
                  fill=(207, 199, 238, 255))
    draw.rounded_rectangle((19, 267, 145, 298), radius=8, fill=(87, 75, 156, 100),
                           outline=(173, 154, 255, 100), width=1)
    label = "WINDOWS INSTALLER"
    box = draw.textbbox((0, 0), label, font=regular)
    draw.text(((width - box[2]) / 2, 278), label, font=regular, fill=(235, 230, 255, 255))

    destination = build_dir / "wizard.bmp"
    image.save(destination, format="BMP")
    return destination


def make_installing_art(build_dir: Path) -> Path:
    source_path = ROOT / "assets" / "idesktop-install-preview.png"
    source = Image.open(source_path).convert("RGB")
    width, height = 820, 500
    image = Image.new("RGB", (width, height), (19, 19, 39))
    thumbnail = source.copy()
    thumbnail.thumbnail((width - 40, height - 40), Image.Resampling.LANCZOS)
    left = (width - thumbnail.width) // 2
    top = (height - thumbnail.height) // 2
    mask = Image.new("L", thumbnail.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, thumbnail.width - 1, thumbnail.height - 1),
        radius=24,
        fill=255,
    )
    image.paste(thumbnail, (left, top), mask)
    ImageDraw.Draw(image).rounded_rectangle(
        (6, 6, width - 7, height - 7),
        radius=28,
        outline=(153, 123, 245),
        width=4,
    )
    destination = build_dir / "installing-image.png"
    image.save(destination, format="PNG", optimize=True)
    return destination


def find_compiler(explicit: str | None) -> str:
    candidates = [
        explicit,
        os.environ.get("ISCC"),
        shutil.which("ISCC.exe"),
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate))
    raise FileNotFoundError(
        "Inno Setup 6 was not found. Install it from https://jrsoftware.org/isdl.php "
        "or pass --iscc with the path to ISCC.exe."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iscc", help="path to Inno Setup's ISCC.exe")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="compile a non-elevated wizard preview; it must not be used to install iDesktop",
    )
    args = parser.parse_args()
    if sys.platform != "win32" or sys.maxsize <= 2**32:
        raise SystemExit("Build the iDesktop installer on 64-bit Windows.")
    if sys.version_info[:2] != (3, 13):
        raise SystemExit("Build dependencies must be downloaded with 64-bit Python 3.13.")

    compiler = find_compiler(args.iscc)
    with (ROOT / "pyproject.toml").open("rb") as project_file:
        version = tomllib.load(project_file)["project"]["version"]
    build_dir = ROOT / "build" / "installer"
    preview_dir = ROOT / "build" / "installer-preview"
    build_dir.mkdir(parents=True, exist_ok=True)

    try:
        download_python_installer(build_dir / "python-installer.exe")
        build_wheelhouse(build_dir)
        make_wizard_art(build_dir)
        make_installing_art(build_dir)
        command = [
            compiler,
            f"/DAppVersion={version}",
            f"/DBuildDir={build_dir}",
        ]
        if args.preview:
            preview_dir.mkdir(parents=True, exist_ok=True)
            command.extend(
                [
                    "/DInstallPrivileges=lowest",
                    f"/DSetupOutputDir={preview_dir}",
                    "/DSetupOutputName=iDesktop-Installer-Preview",
                ]
            )
        command.append(str(ROOT / "installer" / "idesktop.iss"))
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise
    else:
        shutil.rmtree(build_dir)
        if args.preview:
            output_path = preview_dir / "iDesktop-Installer-Preview.exe"
        else:
            for name in (
                "iDesktop-finished-preview.png",
                "iDesktop-installer-preview.png",
                "iDesktop-installing-preview.png",
                "iDesktop-Installer-Preview.exe",
            ):
                (ROOT / "dist" / name).unlink(missing_ok=True)
            if preview_dir.exists():
                shutil.rmtree(preview_dir)
            output_path = ROOT / "dist" / f"iDesktop-Setup-{version}-x64.exe"
        print(f"Installer created: {output_path}")


if __name__ == "__main__":
    main()
