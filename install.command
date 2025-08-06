#!/usr/bin/env bash
set -e

# Install Python if missing
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found. Attempting to install via Homebrew..."
  if command -v brew >/dev/null 2>&1; then
    brew install python
  else
    echo "Homebrew not found. Please install Homebrew and rerun this script: https://brew.sh"
    exit 1
  fi
fi

# Upgrade pip and install project requirements
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# Install Playwright and browser binaries
pip3 install playwright
python3 -m playwright install

echo "Installation complete."

