"""Syntax-check the JavaScript that viewer_layer.py injects into the viewer page (needs Node.js).
Usage: python tools/check_viewer_js.py"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from idesktop import viewer_layer  # noqa: E402

cutout_checks = {
    "three cutout modes": "['standard', 'pro', 'off'].includes(notchMode)" in viewer_layer.BODY_INJECT,
    "cutout shown over normal mirror": "body.ext-notch-visible #device-frame #ext-notch" in viewer_layer.HEAD_INJECT,
    "cutout follows floating canvas": (
        "moveInto(canvas, extBezel); moveInto(frameNotch, extBezel);" in viewer_layer.BODY_INJECT
    ),
    "floating cutout control": "['notch', () => notchLabel(), cycleNotchMode]" in viewer_layer.BODY_INJECT,
}
missing = [name for name, present in cutout_checks.items() if not present]
if missing:
    print("viewer cutout wiring missing: " + ", ".join(missing))
    sys.exit(1)

js = "\n;\n".join(re.findall(r"<script[^>]*>(.*?)</script>", viewer_layer.HEAD_INJECT + viewer_layer.BODY_INJECT, re.S))
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
Path(f.name).unlink()
if r.returncode:
    print(r.stderr)
    sys.exit(1)
print(f"viewer JS OK ({len(js)} chars)")
