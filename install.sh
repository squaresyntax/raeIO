#!/bin/bash

set -e

if [[ "$(uname)" != "Linux" ]]; then
  echo "This install script is intended for Linux." >&2
  exit 1
fi

echo "Installing Python, pip packages, Playwright, and Bank Gothic font..."

if ! command -v apt-get >/dev/null 2>&1; then
  echo "Error: apt-get not found. Install required packages manually." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y python3 python3-pip fontconfig wget unzip || {
  echo "Error installing system packages." >&2
  exit 1
}

pip3 install -r requirements.txt playwright || {
  echo "Error installing Python packages." >&2
  exit 1
}

playwright install || {
  echo "Error running 'playwright install'." >&2
  exit 1
}

FONT_DIR="$HOME/.fonts"
mkdir -p "$FONT_DIR"
if ! wget -q -O "$FONT_DIR/ShareTechMono-Regular.ttf" https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf; then
  echo "Error downloading font." >&2
  exit 1
fi
fc-cache -fv "$FONT_DIR"

echo "Installation complete."
