# RAE.IO - User-Friendly, Cross-Platform Autonomous Agent

## Features

- **Progressive Disclosure**: Beginner/Advanced modes, context-sensitive help, smart defaults.
- **Guided Onboarding**: Welcome tour, quickstart guide, help icons on all controls.
- **Smart Defaults/Personalization**: Remembers your last settings; save your favorite configuration.
- **Real-Time Feedback**: Progress spinners, success/error alerts, task logs.
- **Accessibility**: Responsive UI, keyboard/screen reader friendly.
- **Undo/Clear**: Manual cache/temp clear, session reset.
- **Advanced Analytics**: Agent performance, task memory, error tracking.
- **Talkback/TTS**: Selectable voices/tonality, instant output playback.
- **Plugin System**: Extend with your own Python plugins.
- **Mobile/Desktop/PWA**: Add to homescreen on iOS/Android, one-click desktop install.
- **User Testing/Analytics (opt-in)**: Help improve the app by sending anonymous stats.

## Installation

### Linux & macOS

Run the provided shell script which will detect your OS, ensure Python 3 is available, install required system packages (fonts and audio libraries), Python dependencies, and Playwright browsers:

```bash
./install.sh
```

macOS users can also double-click `install.command` from Finder.

### Windows

Open `install.bat` and follow the prompts. The script verifies Python 3, installs missing audio libraries (ffmpeg) and fonts, installs the Python dependencies from `requirements.txt`, and runs `playwright install`.

## Quickstart

After installation, start the UI:

1. `streamlit run ui.py`
2. [Optional] Use PyInstaller or Briefcase for a desktop app.
3. For mobile, open the app in your browser and "Add to Homescreen".

## CLI Usage

Run the CLI with a prompt. By default it operates in **Text** mode when no `--mode` is supplied:

```bash
python raeio_cli_Version2.py --prompt "Write a short poem about the sky"
```

## Running Tests

1. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install pytest
   ```
2. Run the test suite:
   ```
   pytest
   ```

## UX Best Practices Used

- **Onboarding**: Immediate welcome, quickstart, in-app docs.
- **Progressive Disclosure**: Beginner/Advanced modes, hide advanced until needed.
- **Realtime Feedback**: Spinners, log panel, clear error messages.
- **Personalization**: Save/load user settings, remember last-used options.
- **Accessibility**: Responsive, large buttons, mobile/PWA ready.
- **Undo/Clear**: Manual cache/temp clear, session reset.
- **Help/Docs**: Help expander, tooltips, external docs links.
- **Performance**: Auto cache management, responsive UI, async tasks.
- **Analytics**: Opt-in only, privacy-safe.

## Notes

- **No features have been removed for simplicity** — everything is just contextually organized.
- **All advanced features remain** but are hidden by default for new users.
- **All error messages are user-friendly** and actionable.
- **All code has been bug-checked and tested for modularity and reliability**.

---