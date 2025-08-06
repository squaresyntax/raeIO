#!/bin/bash
echo "Installing Python, pip, dependencies, and Bank Gothic font..."

# macOS
brew install python3
pip3 install -r requirements.txt

# Install Bank Gothic font (use free Share Tech Mono for demo)
mkdir -p ~/Library/Fonts
curl -Lo ~/Library/Fonts/ShareTechMono-Regular.ttf https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf

echo "Installation complete."