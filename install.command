#!/bin/bash
# macOS wrapper that defers to install.sh after ensuring the OS is correct.

if [[ "$(uname)" != "Darwin" ]]; then
    echo "This installer is intended to be run on macOS."
    exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$DIR/install.sh"

