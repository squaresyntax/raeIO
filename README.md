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

1. `pip install streamlit TTS playwright pyyaml`
2. `playwright install`
3. `streamlit run ui.py`
4. [Optional] Use PyInstaller or Briefcase for desktop app.
5. For mobile, open the app in your browser and "Add to Homescreen".

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

## Safety Filters and Legal Considerations

The project includes several safety mechanisms such as PII redaction, NSFW content checks, and action whitelisting.
These safeguards are enabled by default (`enable_pii_filter`, `enable_nsfw_filter`, `enforce_action_whitelist` set to `true`) to help prevent misuse and comply with applicable laws and platform policies.

You may disable these filters through the `safety_filters` and `security` sections of `config.yaml`, but doing so may expose you to legal liabilities and ethical concerns.
Users are solely responsible for any content generated or actions performed when safeguards are disabled.