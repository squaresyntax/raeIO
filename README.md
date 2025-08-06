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

Run the installer for your platform to set up Python, project requirements, and Playwright browsers.

### Linux
```
chmod +x install.sh
./install.sh
```

### macOS
```
chmod +x install.command
./install.command
```

### Windows
Double-click `install.bat` in Explorer or run:
```
install.bat
```

## Packaging

### Desktop (Windows/macOS/Linux)
Use [PyInstaller](https://www.pyinstaller.org/) to bundle the app into a standalone executable:
```
pip install pyinstaller
pyinstaller launch_raeio.spec
```

### Mobile (Android/iOS)
The project can be packaged with tools like [Kivy](https://kivy.org/) or [Buildozer](https://github.com/kivy/buildozer). Refer to their documentation for platform-specific instructions.

## Quickstart

1. `streamlit run ui.py`
2. [Optional] Use PyInstaller or Briefcase for desktop app.
3. For mobile, open the app in your browser and "Add to Homescreen".

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
