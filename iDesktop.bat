@echo off
setlocal
set "IDESKTOP_HOME=%~dp0"
set "IDESKTOP_CODE_HOME=%IDESKTOP_HOME%"
set "IDESKTOP_PYTHON="

if exist "%IDESKTOP_HOME%Others\idesktop\app.py" set "IDESKTOP_CODE_HOME=%IDESKTOP_HOME%Others"

if exist "%IDESKTOP_HOME%runtime\pythonw.exe" set "IDESKTOP_PYTHON=%IDESKTOP_HOME%runtime\pythonw.exe"
if not defined IDESKTOP_PYTHON if exist "%IDESKTOP_HOME%runtime\Scripts\pythonw.exe" set "IDESKTOP_PYTHON=%IDESKTOP_HOME%runtime\Scripts\pythonw.exe"
if not defined IDESKTOP_PYTHON if exist "%IDESKTOP_HOME%venv\Scripts\pythonw.exe" set "IDESKTOP_PYTHON=%IDESKTOP_HOME%venv\Scripts\pythonw.exe"
if not defined IDESKTOP_PYTHON if exist "%IDESKTOP_HOME%..\venv\Scripts\pythonw.exe" set "IDESKTOP_PYTHON=%IDESKTOP_HOME%..\venv\Scripts\pythonw.exe"
if not defined IDESKTOP_PYTHON if exist "%LOCALAPPDATA%\iDesktop\venv\Scripts\pythonw.exe" set "IDESKTOP_PYTHON=%LOCALAPPDATA%\iDesktop\venv\Scripts\pythonw.exe"

if not defined IDESKTOP_PYTHON (
    echo iDesktop's Python environment was not found. Run the installer again.
    pause
    exit /b 1
)

pushd "%IDESKTOP_CODE_HOME%"
start "" "%IDESKTOP_PYTHON%" -m idesktop.splash %*
popd
