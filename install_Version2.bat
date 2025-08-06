@echo off
echo Installing RAE.IO Desktop...

REM Check for Python (for fallback/advanced)
where python
IF ERRORLEVEL 1 (
    echo Python not found. Skipping Python install.
) ELSE (
    pip install -r app/requirements.txt
)

REM Build EXE if not present
IF NOT EXIST "dist\RAEIO.exe" (
    pip install pyinstaller
    pyinstaller --onefile --windowed --name RAEIO app\raeio_app.py
)

REM Copy EXE to root folder
copy dist\RAEIO.exe RAEIO.exe

echo Install complete.
pause