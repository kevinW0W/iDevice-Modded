from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheelhouse", required=True, type=Path)
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("w", encoding="utf-8", errors="replace") as log:
        log.write(f"Runtime: {sys.executable}\n")
        log.write(f"Version: {sys.version}\n")
        if sys.version_info[:2] != (3, 13) or sys.maxsize <= 2**32:
            log.write("Expected 64-bit Python 3.13.\n")
            return 1
        if not args.wheelhouse.is_file() or not args.requirements.is_file():
            log.write("The bundled wheelhouse or requirements file is missing.\n")
            return 1

        try:
            with tempfile.TemporaryDirectory(prefix="iDesktop-wheels-") as tmp:
                wheel_dir = Path(tmp).resolve()
                with zipfile.ZipFile(args.wheelhouse) as archive:
                    for member in archive.infolist():
                        target = (wheel_dir / member.filename).resolve()
                        if not target.is_relative_to(wheel_dir):
                            raise ValueError(f"Unsafe wheelhouse path: {member.filename}")
                    archive.extractall(wheel_dir)
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--no-index",
                        "--disable-pip-version-check",
                        "--find-links",
                        str(wheel_dir),
                        "-r",
                        str(args.requirements),
                    ],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            log.write(f"Dependency installation failed: {type(exc).__name__}: {exc}\n")
            return 1

        if result.returncode:
            log.write(f"pip exited with status {result.returncode}.\n")
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
