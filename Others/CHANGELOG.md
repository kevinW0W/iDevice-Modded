# Changelog

## 0.1.9

### What's Fixed

- Remember the startup splash and Edge mirror positions between launches.
- Restore saved windows on a connected monitor and clamp off-screen positions after monitor changes.
- Removed the separate VBS shortcut helper; shortcuts now launch the windowless Python runtime directly.
- Replaced the splash's native Windows title bar with custom draggable chrome and matching minimize/close controls.

## 0.1.8

- Made the startup splash draggable from its Windows title bar and custom header.
- Removed the always-on-top behavior and added a minimize button so the splash can get out of the way.

## 0.1.7

- Fixed the floating mirror restoring itself about 10 seconds after it was minimized; periodic layout updates are now deferred while the window is minimized.
- Rebranded the Windows installer as iDevice Modded.

## 0.1.6

- The Edge app window now opens centered in the usable desktop area, accounting for display scaling and the taskbar.

## 0.1.5

- Fixed wheel scrolling in landscape by rotating scroll gestures to match the visible screen direction.
- The startup splash now opens centered, can be dragged by its header, and starts iDesktop without showing a console window.
- Start Menu and desktop shortcuts open the splash without showing a console window.

## 0.1.4

- Start Menu and desktop shortcuts now install the repository-root `iDesktop.bat` launcher, which launches the app directly and supports both checkout and installed layouts.

## 0.1.3

- Changed Pro Notch to a clear on/off toggle in the normal and floating controls.
- Pro Notch now follows the mirrored display as it rotates.
- Floating power and volume buttons now rotate with the phone instead of disappearing in landscape.

## 0.1.2

- Fixed the Pro Dynamic Island overlay so it stays aligned over the mirrored screen in both normal and floating views.
- Added a saved cutout selector in the normal and floating controls.
- Resized the Pro Dynamic Island to better match the proportions of the real cutout.

## 0.1.1

- Start Menu and desktop shortcuts now launch the installed `iDesktop.bat`, which selects the correct private Python runtime. The PowerShell install and repository-root launcher use the same batch entry point.

## Unreleased

- Quitting (and Disconnect) now ends Automation on the phone right away: iDesktop kills the WebDriverAgent runner on the phone before exiting, so "Automation Running" goes away at once instead of lingering. Your on/off choice is kept for next time.
- Root cause of WebDriverAgent connections stalling after a client disconnects: the tunnel's TCP stack reused the same source port for every connection to the phone, so a new connection collided with the one iOS was still closing. Each connection now gets a random port.
- New connections to the phone through the no-admin tunnel (WebDriverAgent requests, for one) no longer hang forever when the phone stops answering new connections: each gets 6 s, one retry, then a quick error. Timeouts are logged.
- Passcode keypad opens far less often: once when Automation starts and iOS asks, or when you click the mirror of a locked phone - no longer on every lock or whenever WebDriverAgent is slow. Its keys ignore clicks for half a second after it appears.
- Passcode keypad clears the phone's passcode field before each new code, and has a button that opens the Enter Passcode screen.
- The keyboard button is a plain Show / hide toggle: iOS doesn't report the state, and the guessed on/off label could be backwards.
- App Switcher works: it's a double press of Home now (iOS ignores edge swipes from the HID touch input). The home bar opens it on double-click, drag up or right-click.
- Turning PC sound on drops the phone's volume to its lowest step; volume uses the phone's own keys, no Automation needed.
- Passcode keypad: waits until the phone has stayed locked for a moment, wakes the passcode entry before the first digit, sends keys strictly one at a time, and doesn't pop back up while a code is being checked.
- Automation's helper threads share one WebDriverAgent session instead of knocking each other's out.

## 0.1.0 (first public release)

- HD mirror (iOS 27+): the iPhone's own HEVC stream at up to 60 fps, drawn sharp at window resolution.
- Floating phone window, with a titanium rim and working side buttons; floating glass controls; Big Screen and Desktop Mode.
- Touch, drag, scroll and pinch; PC keyboard with Alt as ⌘; on-screen keyboard toggle (Ctrl+K).
- Phone audio on the PC (FFmpeg AAC-ELD decoder), with a "Sound on PC only" option.
- Two-way clipboard sync.
- Wireless: no cable and no admin rights after one wired start. It finds the phone on the network without Bonjour and reconnects by itself.
- Auto-rotate for landscape apps.
- Lite mode that keeps the mirror live and controllable during calls (WebDriverAgent, an optional extra).
- One-line installer, uninstaller, and a first-run guide (Trust, Developer Mode, developer disk image).
