#!/bin/bash

set -e

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This install script is intended for macOS." >&2
  exit 1
fi

echo "Installing Python, pip packages, Playwright, and Bank Gothic font..."

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required but was not found. Install Homebrew and rerun." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  brew install python
fi

pip3 install -r requirements.txt playwright || {
  echo "Error installing Python packages." >&2
  exit 1
}

playwright install || {
  echo "Error running 'playwright install'." >&2
  exit 1
}

FONT_DIR="$HOME/Library/Fonts"
mkdir -p "$FONT_DIR"
if ! curl -L -o "$FONT_DIR/ShareTechMono-Regular.ttf" https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf; then
  echo "Error downloading font." >&2
  exit 1
fi

echo "Installation complete."
