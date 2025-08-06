@echo off
setlocal

echo Detecting operating system...
ver | findstr /i "Windows" >nul
if errorlevel 1 (
    echo This script is intended for Windows.
    exit /b 1
)

REM Ensure Python 3
where python >nul 2>&1
if errorlevel 1 (
    echo Python 3 not found. Attempting to install via winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo winget not found. Please install Python 3 manually from https://www.python.org/downloads/ and re-run.
        exit /b 1
    )
    winget install -e --id Python.Python.3
)

REM Check audio library (ffmpeg)
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo ffmpeg (required for audio) not found. Attempting to install via winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo winget not found. Please install ffmpeg manually and re-run.
    ) else (
        winget install -e --id Gyan.FFmpeg
    )
)

REM Install fallback font if missing
if not exist "%WINDIR%\Fonts\ShareTechMono-Regular.ttf" (
    echo Installing Share Tech Mono font...
    powershell -Command "Invoke-WebRequest -OutFile $env:WINDIR\Fonts\ShareTechMono-Regular.ttf https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf"
) else (
    echo Required fonts already present.
)

REM Install Python dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install

echo Installation complete.
pause
