# RAE.IO Install Guide

## Windows
- Run `install.bat`
- Installs Python 3.10+, pip, dependencies, Bank Gothic font, and creates Start Menu shortcut.

## macOS
- Run `install.command`
- Installs Homebrew, Python, pip, dependencies, Bank Gothic font, and Applications shortcut.

## Linux
- Run `install.sh`
- Installs Python, pip, system dependencies, Bank Gothic font, and .desktop entry.
- Supports Debian/Ubuntu, Fedora, Arch.

## Web / Portable
- Use included Dockerfile:
    - `docker build -t raeio .`
    - `docker run -p 8501:8501 -v $(pwd)/data:/app/data raeio`

---