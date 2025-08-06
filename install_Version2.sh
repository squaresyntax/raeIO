#!/bin/bash
echo "Installing RAE.IO Desktop..."

python3 -m pip install -r app/requirements.txt

echo "To run, use: python3 app/raeio_app.py"
echo "For Windows, use RAEIO.exe"