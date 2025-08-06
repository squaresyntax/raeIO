#!/usr/bin/env bash
set -e

# Install Python if missing
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found. Attempting to install..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
  else
    echo "Please install Python 3 manually and re-run this script."
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
