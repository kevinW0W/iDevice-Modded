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
    "binary Pro Notch label": "'Pro Notch: ' + (proNotch ? 'on' : 'off')" in viewer_layer.BODY_INJECT,
    "no three-state cutout cycle": "cycleNotchMode" not in viewer_layer.BODY_INJECT,
    "cutout shown over normal mirror": "body.ext-notch-visible #device-frame #ext-notch" in viewer_layer.HEAD_INJECT,
    "cutout follows floating canvas": (
        "moveInto(canvas, extBezel); moveInto(frameNotch, extBezel);" in viewer_layer.BODY_INJECT
    ),
    "floating cutout toggle": (
        "['notch', () => notchLabel(), toggleProNotch]" in viewer_layer.BODY_INJECT
        and "notchButton.addEventListener('click', toggleProNotch)" in viewer_layer.BODY_INJECT
    ),
    "rotated cutout placement": "const rotation = ((visualRotation % 360) + 360) % 360" in viewer_layer.BODY_INJECT,
    "rotated side buttons": "if (visualRotation === 90)" in viewer_layer.BODY_INJECT,
    "power button remains visible in landscape": "if (sideways || !(pos >= 0))" not in viewer_layer.BODY_INJECT,
}
missing = [name for name, present in cutout_checks.items() if not present]
if missing:
    print("viewer cutout wiring missing: " + ", ".join(missing))
    sys.exit(1)

wheel_helper = re.search(
    r"  function wheelDeltaToDevice\(dx, dy, rotation\) \{.*?\n  \}",
    viewer_layer.BODY_INJECT,
    re.S,
)
if not wheel_helper:
    print("viewer wheel-rotation helper is missing")
    sys.exit(1)
wheel_tests = """
const assert = require('node:assert/strict');
assert.deepEqual(wheelDeltaToDevice(0, 1, 0), [0, 1]);
assert.deepEqual(wheelDeltaToDevice(0, 1, 90), [1, 0]);
assert.deepEqual(wheelDeltaToDevice(0, 1, -90), [-1, 0]);
assert.deepEqual(wheelDeltaToDevice(0, 1, 180), [0, -1]);
assert.deepEqual(wheelDeltaToDevice(1, 0, 90), [0, -1]);
"""
result = subprocess.run(
    ["node", "-e", wheel_helper.group(0) + "\n" + wheel_tests],
    capture_output=True,
    text=True,
)
if result.returncode:
    print(result.stderr)
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
