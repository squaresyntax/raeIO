@echo off
REM Install Python if missing
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python3 not found. Please install it from https://www.python.org/downloads/ and re-run this script.
    pause
    exit /b 1
)

REM Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright and browser binaries
pip install playwright
python -m playwright install

echo Installation complete.
pause
