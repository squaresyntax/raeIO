# Energy Transformer AI - User Interface

## Features

- **Beginner/Advanced Modes:** Simple guided steps for new users, full control for advanced users.
- **Undetectable Mode:** One-click switch for stealth/anonymity (proxy, ephemeral logging, session isolation).
- **Real-Time Problem Solving:** Async task queue for multi-modal generation—never blocks UI.
- **Output Gallery:** View latest generated images, videos, and audio.
- **Live Logs:** See progress, errors, and completion in real time.
- **Resource Monitor:** CPU and Memory usage shown in sidebar.
- **Config Upload/Download:** Power users can upload or download full agent configs.

## How to Run

1. Ensure dependencies:  
   `pip install streamlit pyyaml`  
   (Optional for resource panel: `pip install psutil`)

2. Start the UI:  
   `streamlit run ui.py`

3. Interact in your browser (default: http://localhost:8501)

## Extending

- Add new tabs or controls as you add browser automation, plugins, etc.
- “Undetectable Mode” can be further enhanced with more advanced fingerprinting and anti-detection measures in your agent logic.

## Security Note

- “Undetectable” is for privacy/anonymity; always use ethically and legally.