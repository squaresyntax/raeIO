@echo off
IF /I NOT "%OS%"=="Windows_NT" (
    echo This install script is intended for Windows.
    exit /B 1
)

echo Installing Python, dependencies, Playwright, and Bank Gothic font...

where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python 3.10+ is required. Please install Python and rerun.
    pause
    exit /B 1
)

pip install -r requirements.txt playwright || (
    echo Failed to install Python packages.
    exit /B 1
)

python -m playwright install || (
    echo Playwright browser installation failed.
    exit /B 1
)

powershell -Command "try { $dest=\"$env:WINDIR\Fonts\ShareTechMono-Regular.ttf\"; Invoke-WebRequest -OutFile $dest https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf } catch { exit 1 }" >nul
IF ERRORLEVEL 1 (
    echo Failed to download font.
    exit /B 1
)

echo Installation complete.
pause
