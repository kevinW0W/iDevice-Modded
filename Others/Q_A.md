# iDesktop Help and Troubleshooting

This guide covers common setup, connection, display, input, audio, and development problems.
Try the steps in order and stop when the problem is fixed. Menu labels may differ slightly
between Windows releases.

> **Privacy:** logs and screenshots can reveal your Windows username, iPhone name, device
> identifiers, IP addresses, notifications, or messages. Review and redact them before sharing.

## Contents

- [Before you start](#before-you-start)
- [Install and update](#install-and-update)
- [Connect the iPhone](#connect-the-iphone)
- [Mirror and display](#mirror-and-display)
- [Controls and sound](#controls-and-sound)
- [Automation and Lite mode](#automation-and-lite-mode)
- [Logs and reports](#logs-and-reports)
- [Build and development](#build-and-development)

## Before you start

### 1. What does iDesktop do?

iDesktop mirrors an iPhone on a Windows PC and sends mouse and keyboard input back to the phone.
It can show the phone in a normal viewer window or a movable floating-phone window. Audio and
clipboard features are also available.

### 2. Which iPhone and iOS versions are supported?

The HD stream uses Apple's CoreDevice DisplayService, available to this project on iOS 27 and
newer. Older iOS versions may use the optional WebDriverAgent-based Lite viewer instead. Results
depend on the exact iOS release and setup; report the model and full version when asking for help.

### 3. What does “Lite mode” mean?

Lite mode is the WebDriverAgent screen-view fallback, not a separate paid or reduced edition.
It may be used on older iOS releases or during calls when iOS blocks the HD stream. It has lower
frame rate and resolution. Install and start the optional WebDriverAgent helper to use it.

### 4. What does the startup splash do?

The splash stays visible while iDesktop starts and connects to the phone. Its progress indicator
is animated, not an exact percentage. The log panel shows recent startup messages; if the app
stops, leave the splash open and use those messages when troubleshooting.

### 5. What are the minimum PC requirements?

Use 64-bit Windows 10 version 1809 or newer, or Windows 11, and Microsoft Edge. HD video also
requires a GPU that can decode HEVC; many PCs need Microsoft's HEVC Video Extensions. The Windows
installer includes the app's Python dependencies.

### 6. Do I need Python before installing?

The Windows installer looks for compatible 64-bit Python 3.13 and reuses it when available.
Otherwise it can install its bundled Python privately. The PowerShell development installer has
different runtime handling; follow its own prompts and consult [Install and update](#install-and-update).

### 7. Does iDesktop send my screen or data to a cloud service?

The app's phone connection and viewer run locally between your PC and iPhone. The installer may
use the Microsoft Store for the optional Apple Devices app, and first-run iOS setup can download
Apple developer support files. Do not share logs publicly without checking them for personal data.

### 8. Which cable should I use?

Use a USB cable that supports data, not a charge-only cable. Connect directly to a working PC port
while diagnosing; avoid hubs and docks until a direct connection succeeds.

## Install and update

### 9. Where should I download the installer?

Use the setup executable attached to a release of the repository you trust. Check that the release
belongs to the intended project and avoid installers from file-sharing mirrors or unsolicited links.

### 10. Windows says the installer is from an unknown publisher. Is that a failure?

This project may distribute unsigned setup builds, so Windows can show a reputation warning.
Before proceeding, verify the download came from the expected GitHub release and that the file name
matches the release. Cancel if the source is uncertain.

### 11. Setup asks for administrator permission. Why?

The Windows installer targets Program Files and registers an uninstall entry, which require
administrator permission. If you do not want an elevated install, use the project's PowerShell
installer instead and follow its per-user setup instructions.

### 12. The installer says Python 3.13 is already installed. What does that mean?

The bundled wheelhouse is built for 64-bit Python 3.13, so the installer only reuses a compatible
runtime. If the checkbox is unchecked, setup creates a private iDesktop virtual environment using
that detected interpreter; your system interpreter is not used to install the app's packages.

### 13. Python detection looks wrong or the checkbox is disabled. What can I do?

1. Open PowerShell and run `py -0p` to list registered Python runtimes.
2. Check that a 64-bit Python 3.13 interpreter runs with `py -3.13-64 -c "import struct,sys; print(sys.version); print(struct.calcsize('P')*8)"`.
3. If the command reports another version or 32 bits, leave the bundled-Python option enabled.
4. Do not remove another Python installation just to satisfy iDesktop.

### 14. Dependency installation failed during setup. What should I collect?

1. Open `%APPDATA%\iDesktop\logs`.
2. Read `installer-dependencies.log` and, if Python setup ran, `python-install.log`.
3. Note the displayed exit code and the first pip error above the final failure line.
4. Retry the installer once; if the same error returns, attach the relevant redacted logs to a bug report.

### 15. Setup cannot write to Program Files.

Close other setup windows and run the installer using an account allowed to install applications.
Check that security software has not blocked the setup process. Do not work around Windows access
controls by changing permissions on the whole Program Files directory.

### 16. How do I update iDesktop?

Download and run the newer official setup. The installer updates the app in its install location.
Keep `%APPDATA%\iDesktop` intact if you want to preserve pairing/configuration and logs.

### 17. How do I uninstall iDesktop?

Use **Settings > Apps > Installed apps > iDesktop > Uninstall**, or the Start Menu uninstall
shortcut if it was created. The installer may leave user settings and logs in `%APPDATA%\iDesktop`;
remove those separately only if you intentionally want to erase them.

### 18. The Start Menu shortcut is missing.

The installer offers an **Add iDesktop to the Start Menu** option. If it was unchecked, rerun setup
and enable it. You can also launch from the installation directory or create a shortcut to the
installed launcher without moving the app files.

### 19. The desktop shortcut is missing.

The desktop shortcut is optional. Rerun setup and enable the desktop shortcut option, or open
Start and search for iDesktop if its Start Menu shortcut was installed.

### 20. Apple Devices did not install automatically.

1. Install **Apple Devices** from the Microsoft Store.
2. Open it once and allow it to finish setup.
3. Reconnect and unlock the iPhone.
4. If the app is unavailable in your region or Store, consult Apple's supported Windows device
   software options; do not download driver packages from untrusted sites.

## Connect the iPhone

### 21. iDesktop says no iPhone was found.

1. Unlock the iPhone and keep it awake.
2. Connect a known data cable directly to the PC.
3. Accept **Trust This Computer?** on the phone and enter its passcode.
4. Confirm Apple Devices or iTunes is installed.
5. Try another cable and USB port, then restart iDesktop.
6. If it still fails, inspect `launcher.log` in `%APPDATA%\iDesktop\logs`.

### 22. The Trust prompt never appears.

Unlock the iPhone, unplug it, and reconnect it. If **Don't Trust** was selected previously, reset
**Settings > General > Transfer or Reset iPhone > Reset > Reset Location & Privacy**, then reconnect
and choose **Trust**. This resets the phone's privacy trust decisions.

### 23. Windows makes a connection sound, but iDesktop cannot find the phone.

The Windows sound only confirms that something connected over USB; it does not prove that the
cable carries data or that Apple device services are working. Try a data cable, open Apple Devices
to see if it recognizes the phone, then check `launcher.log`.

### 24. USB works in Apple Devices but iDesktop does not connect.

1. Unlock the phone and close other tools that may be controlling it.
2. Reconnect the cable and restart iDesktop.
3. Check `launcher.log` for tunnel, pairing, or service errors.
4. Try Wi-Fi only after a successful wired pairing.
5. Include the exact log error in a bug report after redacting device identifiers.

### 25. How do I set up Wi-Fi?

First connect the iPhone over USB and complete the trust/pairing prompts. Then put the PC and phone
on the same local network and start iDesktop without the cable. Wi-Fi can fail on guest, hotel, or
corporate networks that isolate devices from one another.

### 26. Wi-Fi worked before but stopped after changing networks.

1. Confirm the PC and phone are on the same network or reachable subnet.
2. Turn off guest-network/client isolation if you control the access point.
3. Start iDesktop once over USB if pairing needs to be refreshed.
4. Unlock the phone and allow local-network access if iOS asks.
5. Try again on a trusted private network.

### 27. I changed my iPhone passcode. Does that affect connection?

Unlock the phone with the new passcode and reconnect. If pairing remains unavailable, remove and
re-establish the phone trust relationship by resetting **Location & Privacy** and accepting the
trust prompt again. Be aware this resets other privacy permissions too.

### 28. Is a personal hotspot supported?

The PC and iPhone need local IP connectivity to each other. A personal hotspot can work in some
setups, but carrier, Windows, and hotspot isolation behavior varies. Test with both devices on the
same ordinary private Wi-Fi network first.

### 29. The phone disconnects when the cable is removed.

Wireless use requires successful initial pairing and a reachable network. Verify the phone and PC
remain on the same network, then wait for the launcher to retry. Check `launcher.log` for the
selected transport and any network or tunnel errors.

### 30. A firewall prompt appeared. What should I choose?

Allow iDesktop on a trusted **Private** network if Windows asks and you want Wi-Fi connectivity.
Do not enable broad public-network access unless you understand and need it. Never disable the
firewall entirely as a first troubleshooting step.

## Mirror and display

### 31. The iDesktop window is black.

1. Unlock the phone and wait several seconds.
2. Check whether a phone call, FaceTime call, camera, or microphone session is active.
3. Install Microsoft's HEVC Video Extensions if the log mentions HEVC or decoding.
4. Update Windows and your GPU driver from the PC or GPU manufacturer's official source.
5. Click **Refresh** or press F5.
6. Inspect `native.log` and `launcher.log` for decoder or stream errors.

### 32. The picture is frozen, but taps still work.

Click **Refresh** in the viewer or press F5. If the stream does not resume, disconnect and reconnect
the iPhone. A still phone screen may produce few video frames; test by changing the screen on the
phone. If it remains frozen, collect `native.log`.

### 33. Video does not decode or says HEVC is unsupported.

Install [HEVC Video Extensions](https://apps.microsoft.com/detail/9NMZLZ57R3T7), restart iDesktop,
and try again. Confirm the PC GPU supports HEVC decoding and its Windows graphics driver is current.
The installer cannot guarantee that every PC includes a compatible decoder.

### 34. Mirroring pauses during a phone or FaceTime call.

iOS can stop the HD stream while the camera or microphone is in use. With WebDriverAgent installed
and Automation running, iDesktop can use Lite mode during the pause. Otherwise wait for the call to
end; HD should recover when iOS allows the stream again.

### 35. The mirror looks too small or too large.

Use **Bigger / Smaller** or Ctrl+Up / Ctrl+Down. In the normal window, adjust the browser zoom if
needed. Use **Big Screen** for a monitor-filling view; press Esc to leave it.

### 36. The frame notch does not match my iPhone.

The Pro Notch control is a simple **on/off** toggle. When on, the Dynamic Island overlay appears
over the live mirror; when off, it is hidden. The selection is saved, follows screen rotation, and
works in both normal and floating views. It does not change the actual iPhone display.

### 37. The frame looks misaligned or the phone is clipped.

1. Press F5 to reload the viewer layer.
2. Resize the window once, then use **Refresh** if necessary.
3. Exit Big Screen and re-enter it.
4. In floating mode, move the phone away from the screen edge and restore its size with Bigger /
   Smaller.
5. If the issue repeats, include a screenshot and display scaling information in a bug report.

### 38. Floating mode shows a border or captures clicks outside the phone.

Try **Refresh**, then click **Floating Phone** again to leave and re-enter compact mode. Restore the
window if it was maximized or moved between monitors. Include the monitor arrangement and Windows
display scale if the shape remains wrong.

### 39. The phone frame changes but the live picture does not.

The Pro Notch is an overlay drawn above the live mirror; it does not change the phone or the video
stream, and saved screenshots remain unaltered.
If the picture itself is frozen, use the steps for a [black or frozen mirror](#31-the-idesktop-window-is-black).

### 40. Landscape apps appear rotated incorrectly.

Confirm Automation/WebDriverAgent is installed and running. Reconnect the phone and reopen the
landscape app. If it still fails, turn Automation off and on once, then capture `helper.log` and
`native.log`.

## Controls and sound

### 41. Mouse clicks do not reach the iPhone.

Click inside the live screen, not the metal frame or floating controls. Make sure the window is not
showing a disconnected overlay. If only drags fail, update iDesktop and retry with a short drag;
include your mouse type and display scaling if touch mapping remains offset.

### 42. A swipe turns into a tap.

Drag while keeping the pointer held down until the intended endpoint. Avoid releasing immediately
after the first movement. If it happens consistently, reload the page with F5 and describe the
gesture, app, and approximate drag distance in a bug report.

### 43. Right-click does something unexpected.

Right-click on the phone screen performs a long press; holding and dragging can move icons.
Right-click on the floating rim opens the controls. Use the on-screen controls if the target app
uses a context menu in a conflicting way.

### 44. Keyboard shortcuts do not work.

Focus the iDesktop window and try typing in a normal text field. Some shortcuts are intercepted by
Windows or the active app. Alt is mapped to Command for iPhone shortcuts; Windows-key capture can
be toggled with Ctrl+Alt+Shift+Win while iDesktop is focused.

### 45. The iPhone's on-screen keyboard is hidden.

iOS hides its on-screen keyboard while a hardware keyboard is connected. Press Ctrl+K or select
**Show / hide keyboard** in the controls. This toggles the phone keyboard; iDesktop cannot always
detect its actual current state.

### 46. Audio is missing on the PC.

1. Check that PC audio is enabled in the viewer and Windows output is not muted.
2. Try a different iPhone app; Apple Music may protect audio from screen capture.
3. Check whether the phone is in a call, where iOS may change capture behavior.
4. Inspect `native.log` for AAC decoder or audio-session errors.
5. Confirm the correct Windows playback device is selected.

### 47. “Sound on PC only” makes the phone volume change unexpectedly.

The action sends repeated volume-down presses to reach zero and intentionally does not send a
volume-up press afterward. iOS may also mute audio mirrored to the PC at zero. Use the physical
phone buttons to restore its volume if desired.

### 48. Clipboard synchronization does not work.

Check that clipboard sync is enabled in the full viewer panels. Try plain text first, then a small
image. Some apps block copying or image paste. Do not paste passwords or sensitive data while
testing, and do not attach private clipboard contents to an issue.

### 49. Screenshots are missing.

Use **Screenshot** or Ctrl+P, then check the Windows Downloads folder. If Windows redirects
Downloads to OneDrive, check that location too. Try again after a live frame appears.

## Automation and Lite mode

### 50. What is Automation?

Automation is the optional WebDriverAgent helper running on the iPhone. iDesktop uses it for
features such as auto-rotation, pinch, and the fallback viewer during some calls. It is not required
for basic HD mirroring and touch.

### 51. The Automation button is missing.

The button appears only when iDesktop knows about a WebDriverAgent installation. Follow the
optional WebDriverAgent setup in the README. If it is already installed, restart iDesktop and
check `helper.log` for runner startup errors.

### 52. iOS displays “Automation Running.”

This is iOS's notice while the WebDriverAgent test runner is active. Turn Automation off in
iDesktop or stop/quit the helper. Holding both iPhone volume buttons may also stop the test session.

### 53. Where can I find or download the WebDriverAgent IPA?

Download the [unsigned WebDriverAgent 16.12.8 IPA](https://github.com/kevinW0W/iDevice-Modded/releases/download/v0.1.0/WebDriverAgent-16.12.8-unsigned.ipa) from the release, then install it on your iPhone with [Sideloadly](https://sideloadly.io) and your own Apple ID. It is intentionally unsigned: a generic signed IPA could be signed for someone else's Apple account or devices. The IPA is built from Appium's [official v16.12.8 runner package](https://github.com/appium/WebDriverAgent/releases/download/v16.12.8/WebDriverAgentRunner-Runner.zip). To generate it yourself instead, run `powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\iDesktop\app\extras\install-wda.ps1"`; the resulting file is `%APPDATA%\iDesktop\WebDriverAgent.ipa`, and the script opens its folder.

### 54. How do I install WebDriverAgent?

Follow the [optional WebDriverAgent instructions](README.md#optional-extra-webdriveragent).
Building and signing require Apple's developer tools and a valid provisioning setup; iDesktop does
not bypass Apple's signing requirements. A free Apple ID may require more frequent re-signing.

### 55. WebDriverAgent stopped working after several days.

A free provisioning profile commonly expires after a short period. Rebuild and sideload using the
instructions and signing tool you trust. Check the exact runner error in `helper.log`; do not share
certificates, passwords, or provisioning-profile secrets in an issue.

### 56. Lite mode works but is blurry or slow.

Lite mode is a lower-resolution fallback by design. Confirm Automation is running and close other
apps using the phone camera or microphone. When the call ends, the HD stream should return
automatically. Lite mode is not a setting to increase HD quality.

### 57. The passcode keypad is missing during Automation setup.

iOS hides some system keypads from screen mirroring. Use the keypad overlay if it appears, or type
the passcode from the PC keyboard and press Enter. Do not post a screenshot that reveals your
passcode or notifications.

### 58. A password field or its keyboard is hidden while mirroring.

iOS may conceal secure password-entry UI in the mirrored picture for privacy. iDesktop's custom
keypad is only for the iPhone passcode; it does not provide an on-screen password keyboard.
First tap the password field to focus it, then type with the PC keyboard. If you need the iPhone's
software keyboard, press Ctrl+K or choose **Show / hide keyboard** in the controls; iOS can hide it
while a hardware keyboard is connected. If you cannot tell whether the field has focus or the input
was accepted, use the iPhone itself to enter the password rather than guessing. Password characters
may remain masked by design. Do not include passwords in logs, screenshots, or bug reports.

## Logs and reports

### 59. Where are the logs?

Open `%APPDATA%\iDesktop\logs`. Common files include `launcher.log`, `native.log`, and
`helper.log`; installer setup may also create Python or dependency logs. Logs may be overwritten
when a new run starts, so copy the relevant file soon after reproducing the issue.

### 60. Which log should I attach?

For no-device and startup failures, attach `launcher.log`. For video, audio, or stream failures,
attach `native.log`. For WebDriverAgent, window shape, or control-server issues, attach `helper.log`.
For install failures, include the installer dependency/Python log and the setup's own log if present.

### 61. How do I redact a log?

Open it in a text editor and replace your Windows username, iPhone name, device identifiers, local
IP addresses, and private paths with placeholders such as `[REDACTED]`. Keep timestamps, error
messages, and surrounding context. Review screenshots for notifications and account details too.

### 62. What makes a useful bug report?

Use the [Report a problem form](../.github/ISSUE_TEMPLATE/bug_report.yml). Include exact versions,
connection type, ordered reproduction steps, expected behavior, actual behavior, and relevant
redacted logs. Search existing issues first and mention any troubleshooting steps already tried.

### 63. How can I report that iDesktop works?

Use the **It works on my setup** issue form. Include your iPhone/iOS, Windows/GPU, app version,
connection type, and only the features you tested. These reports help build a compatibility record.

## Build and development

### 64. How do I run iDesktop from source?

1. Clone the repository and enter `Others`.
2. Create a 64-bit Python 3.13 environment: `py -3.13 -m venv .venv`.
3. Install dependencies with `.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt`.
4. Run `.venv\Scripts\python -m idesktop`.
5. Connect an unlocked, trusted iPhone for device-dependent testing.

### 65. How do I run the tests?

From `Others`, run:

```powershell
python -m compileall -q idesktop installer tools
python -m pyflakes idesktop installer tools
python tools\smoke_test.py
python tools\check_viewer_js.py
python tools\e2e_test.py
```

The smoke and end-to-end tests do not require a physical phone. The JavaScript check needs Node.js.
These checks passed on this checkout: compilation, lint, smoke tests, viewer JavaScript syntax, and
the end-to-end tests. They do not verify behavior with every iPhone, Windows build, GPU, or network.

### 66. How do I build the Windows installer?

On 64-bit Windows, install Python 3.13, Pillow, and Inno Setup 6. From `Others`, run
`python tools\build_installer.py`. The script downloads the official Python installer, validates
its SHA-256 checksum, builds an offline wheelhouse, and creates the setup executable in `dist`.

### 67. Why is the build downloading files?

The installer build needs the official Python runtime installer and dependency wheels. It verifies
the Python installer checksum and packages the wheels for offline installation by end users. A
successful build should leave the final setup executable in `Others\dist`.

### 68. How do I debug the viewer layer?

`idesktop/viewer_layer.py` is injected into the viewer and can be hot-reloaded by refreshing the
page with F5. Run `python tools\check_viewer_js.py` after editing it. Browser-side errors are sent
to the helper log; include the relevant redacted lines when reporting a regression.

### 69. How do I enable Edge DevTools?

Set `IDESKTOP_DEVTOOLS=9333` before starting iDesktop, then use
`python tools\cdp.py "<JavaScript expression>"`. Keep the debugging port private and disable it
when finished; do not expose it on an untrusted network.

### 70. Where should I report an issue with this modded fork?

Open an issue in the repository where you downloaded the build. Include the fork name and version,
and state whether the issue also happens on upstream iDesktop. This helps maintainers distinguish
fork-specific changes from upstream behavior.

### 71. Where can I suggest a feature?

Search existing issues first, then open a feature request with the problem you are trying to solve,
your proposed behavior, and any constraints. Explain whether it should apply to the normal viewer,
floating view, or both.

### 72. What should I do if these steps do not fix the problem?

Stop before deleting pairing records, changing broad Windows permissions, or disabling security
software. Gather the exact versions, reproduction steps, and redacted relevant logs, then submit a
bug report. If possible, mention whether the same iPhone works with Apple's device software.
