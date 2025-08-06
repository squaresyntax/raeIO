#!/bin/bash

# Cross-platform installation script for Linux and macOS.
# Installs Python, required pip packages, and Playwright browsers.
set -e

echo "Detecting operating system and installing prerequisites..."

OS="$(uname)"

FONT_URL="https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf"

if [[ "$OS" == "Linux" ]]; then
    if ! command -v apt-get >/dev/null 2>&1; then
        echo "Error: this script requires 'apt-get' but it was not found."
        echo "Please install Python and dependencies manually."
        exit 1
    fi
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip fontconfig wget curl
elif [[ "$OS" == "Darwin" ]]; then
    if ! command -v brew >/dev/null 2>&1; then
        echo "Error: Homebrew is required but was not found."
        echo "Install Homebrew from https://brew.sh/ and re-run this script."
        exit 1
    fi
    brew update
    brew install python3 wget curl
else
    echo "Unsupported operating system: $OS"
    echo "This script supports Linux and macOS only."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python3 installation failed or not found in PATH."
    exit 1
fi

if ! command -v pip3 >/dev/null 2>&1; then
    echo "Error: pip3 not found. Ensure Python is installed correctly."
    exit 1
fi

pip3 install -r requirements.txt
python3 -m playwright install

# Install a free font similar to Bank Gothic
if [[ "$OS" == "Linux" ]]; then
    mkdir -p ~/.fonts
    if command -v wget >/dev/null 2>&1; then
        wget -O ~/.fonts/ShareTechMono-Regular.ttf "$FONT_URL"
    elif command -v curl >/dev/null 2>&1; then
        curl -Lo ~/.fonts/ShareTechMono-Regular.ttf "$FONT_URL"
    else
        echo "Warning: neither wget nor curl found; skipping font installation."
    fi
    fc-cache -fv || true
elif [[ "$OS" == "Darwin" ]]; then
    mkdir -p ~/Library/Fonts
    if command -v curl >/dev/null 2>&1; then
        curl -Lo ~/Library/Fonts/ShareTechMono-Regular.ttf "$FONT_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -O ~/Library/Fonts/ShareTechMono-Regular.ttf "$FONT_URL"
    else
        echo "Warning: neither curl nor wget found; skipping font installation."
    fi
fi

echo "Installation complete."

