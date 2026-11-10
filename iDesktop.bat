@echo off
cd /d "%~dp0Others"
start "" "%LOCALAPPDATA%\iDesktop\venv\Scripts\pythonw.exe" -m idesktop.splash %*
