@echo off
REM Windows installation script for RAE.IO

IF NOT "%OS%"=="Windows_NT" (
    echo This installer must be run on Windows.
    exit /b 1
)

echo Detecting Python...
where python >NUL 2>&1
IF ERRORLEVEL 1 (
    echo Python 3.10+ is required but was not found.
    echo Please install Python from https://www.python.org/downloads/windows/ and re-run this script.
    pause
    exit /b 1
)

echo Installing pip packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt || goto :error

echo Installing Playwright browsers...
python -m playwright install || goto :error

REM Install Bank Gothic font substitute (Share Tech Mono)
powershell -Command "try {Invoke-WebRequest -OutFile $env:WINDIR\Fonts\ShareTechMono-Regular.ttf https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf} catch {Write-Host 'Failed to download font.'}"

echo Installation complete.
pause
exit /b 0

:error
echo Installation failed. Check the output above for details.
pause
exit /b 1

