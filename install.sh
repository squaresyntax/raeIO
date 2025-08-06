#!/usr/bin/env bash
set -e

# Detect operating system
OS="$(uname -s)"
echo "Detected OS: $OS"

ensure_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python 3 not found. Attempting to install..."
        case "$OS" in
            Linux*) sudo apt-get update && sudo apt-get install -y python3 python3-pip ;;
            Darwin*) if command -v brew >/dev/null 2>&1; then
                        brew install python3
                     else
                        echo "Homebrew is required to install Python on macOS. Install from https://brew.sh and re-run." >&2
                        exit 1
                     fi ;;
            *) echo "Unsupported OS for automatic Python installation." >&2
               exit 1 ;;
        esac
    fi
}

install_linux_packages() {
    missing=false
    if ! dpkg -s fontconfig >/dev/null 2>&1; then
        echo "fontconfig (for fonts) not found. Installing..."
        sudo apt-get install -y fontconfig || missing=true
    fi
    if ! dpkg -s libasound2 >/dev/null 2>&1; then
        echo "libasound2 (for audio) not found. Installing..."
        sudo apt-get install -y libasound2 || missing=true
    fi
    if [ "$missing" = true ]; then
        echo "Some system packages failed to install. Please install them manually and re-run." >&2
        exit 1
    fi
}

install_macos_packages() {
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew is required for installing dependencies. Install from https://brew.sh and re-run." >&2
        exit 1
    fi
    missing=()
    if ! brew list --versions fontconfig >/dev/null 2>&1; then
        missing+=(fontconfig)
    fi
    if ! brew list --versions portaudio >/dev/null 2>&1; then
        missing+=(portaudio)
    fi
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Installing missing packages: ${missing[*]}"
        brew install "${missing[@]}" || {
            echo "Failed to install system packages: ${missing[*]}. Please install them manually." >&2
            exit 1
        }
    fi
}

install_python_packages() {
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    python3 -m playwright install
}

case "$OS" in
    Linux*)
        ensure_python
        install_linux_packages
        install_python_packages
        ;;
    Darwin*)
        ensure_python
        install_macos_packages
        install_python_packages
        ;;
    *)
        echo "Unsupported operating system: $OS" >&2
        exit 1
        ;;
esac

echo "Installation complete."
