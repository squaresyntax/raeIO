import os
import sys
import logging
import traceback
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# Import your agent and modules
try:
    from raeio_agent import RAEIOAgent
except Exception:  # pragma: no cover - fallback stub
    class RAEIOAgent:  # type: ignore
        def __init__(self, config, logger):
            pass

        def run_task(self, task_type, prompt, context, plugin=None):
            return f"Stub output for {task_type}: {prompt}"

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

MODES = [
    "Art",
    "Sound",
    "Video",
    "Text",
    "TCG",
    "Fuckery",
    "Training",
    "Browser",
]


def load_config():
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print("Config file not found. Please ensure config.yaml exists.")
        sys.exit(1)
    if yaml:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

def cli_main(agent):
    import argparse
    parser = argparse.ArgumentParser(description="RAE.IO CLI")
    parser.add_argument(
        '--mode',
        choices=MODES,
        help='Operation mode',
        default=None,
    )
    parser.add_argument('--prompt', type=str, help='Prompt for generation/analysis')
    parser.add_argument('--url', type=str, help='URL for browser automation')
    parser.add_argument('--actions', type=str, help='Browser actions as JSON list')
    parser.add_argument('--plugin', type=str, help='Plugin name (optional)')
    args = parser.parse_args()

    if not args.mode:
        if sys.stdin.isatty():
            try:
                user_mode = input("Select mode [Text]: ").strip()
                args.mode = user_mode or 'Text'
            except EOFError:
                args.mode = 'Text'
        else:
            args.mode = 'Text'

    if args.mode == "Browser":
        import json

        if not args.url or not args.actions:
            print("For browser mode, provide --url and --actions (as JSON list)")
            return
        actions = json.loads(args.actions)
        context = {"url": args.url, "actions": actions}
        output = agent.run_task("browser", args.prompt or "", context)
    else:
        context = {}
        output = agent.run_task(
            args.mode.lower(), args.prompt or "", context, plugin=args.plugin
        )
    print(f"\nOutput:\n{output}\n")

def desktop_main(agent):
    # Tkinter desktop UI
    root = tk.Tk()
    root.title("RAE.IO Desktop")

    # Mode selection
    mode_var = tk.StringVar(value="Art")
    mode_box = ttk.Combobox(root, textvariable=mode_var, values=[
        "Art", "Sound", "Video", "Text", "TCG", "Fuckery", "Training", "Browser"
    ], state="readonly")
    mode_box.pack(pady=5)

    # Prompt input
    prompt_label = tk.Label(root, text="Prompt / Query:")
    prompt_label.pack()
    prompt_entry = tk.Entry(root, width=50)
    prompt_entry.pack(pady=5)

    # Browser controls
    url_label = tk.Label(root, text="Browser URL (optional):")
    url_label.pack()
    url_entry = tk.Entry(root, width=50)
    url_entry.pack(pady=5)
    actions_label = tk.Label(root, text="Browser Actions (JSON list, optional):")
    actions_label.pack()
    actions_entry = tk.Entry(root, width=50)
    actions_entry.pack(pady=5)

    # Plugin selection
    plugin_label = tk.Label(root, text="Plugin name (optional):")
    plugin_label.pack()
    plugin_entry = tk.Entry(root, width=50)
    plugin_entry.pack(pady=5)

    # Output display
    output_text = tk.Text(root, height=15, width=60, wrap="word")
    output_text.pack(pady=10)

    def run_task():
        mode = mode_var.get()
        prompt = prompt_entry.get().strip()
        url = url_entry.get().strip()
        actions = actions_entry.get().strip()
        plugin = plugin_entry.get().strip() or None
        context = {}

        try:
            if mode == "Browser":
                import json
                if not url or not actions:
                    output_text.insert(tk.END, "Error: For browser mode, provide URL and actions (JSON list)\n")
                    return
                context = {"url": url, "actions": json.loads(actions)}
                result = agent.run_task("browser", prompt, context)
            else:
                result = agent.run_task(mode.lower(), prompt, context, plugin=plugin)
            output_text.insert(tk.END, f"Output:\n{result}\n\n")
        except Exception as e:
            output_text.insert(tk.END, f"Error: {e}\n{traceback.format_exc()}\n\n")

    run_btn = tk.Button(root, text="Run Task", command=run_task)
    run_btn.pack(pady=10)

    root.mainloop()

def main():
    config = load_config()
    logger = logging.getLogger("RAEIO_APP")
    agent = RAEIOAgent(config, logger)

    # Detect mode by argument or default to desktop GUI
    if "--cli" in sys.argv or not GUI_AVAILABLE:
        cli_main(agent)
    else:
        desktop_main(agent)

if __name__ == "__main__":
    main()
