#!/bin/bash
echo "Installing Python, pip, dependencies, and Bank Gothic font..."

# Linux (Debian/Ubuntu example)
sudo apt-get update
sudo apt-get install -y python3 python3-pip fontconfig wget unzip
pip3 install -r requirements.txt

# Install Bank Gothic font (use a free similar font for demo)
mkdir -p ~/.fonts
wget -O ~/.fonts/ShareTechMono-Regular.ttf https://github.com/google/fonts/raw/main/ofl/sharetechmono/ShareTechMono-Regular.ttf
fc-cache -fv

echo "Installation complete."