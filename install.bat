@echo off
echo Installing Python, pip, dependencies, and Bank Gothic font...

REM Windows
where python
IF ERRORLEVEL 1 (
    echo Please install Python 3.10+ before running this script.
    pause
    exit /b
)
pip install -r requirements.txt

REM Install Bank Gothic font (use Share Tech Mono as fallback)
powershell -Command "Invoke-WebRequest -OutFile %WINDIR%\Fonts\ShareTechMono-Regular.ttf https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf"

echo Installation complete.
pause