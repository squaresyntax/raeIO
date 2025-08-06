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

## Quickstart

1. `pip install streamlit TTS pyyaml`
2. `streamlit run ui.py`
3. [Optional] Use PyInstaller or Briefcase for desktop app.
4. For mobile, open the app in your browser and "Add to Homescreen".

### Browser automation example

The ``BrowserAutomation`` helper can execute simple multi‑page workflows using a
minimal HTTP-based engine.  A script consists of a list of action dictionaries:

```python
from browser_automation import BrowserAutomation

actions = [
    {"type": "query", "selector": "a.login", "store": "links"},
    {"type": "navigate", "from": "links", "index": 0},
    {"type": "type", "selector": "#username", "value": "alice"},
    {"type": "click", "selector": "#submit"},
    {"type": "extract", "selector": "h1", "store": "headers"},
]

result = BrowserAutomation().run_script("https://example.com", actions)
print(result["data"]["headers"])  # extracted text
```

Tests in ``tests/test_browser_automation.py`` show how to automate form
autofill and conditional multi‑page navigation.

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