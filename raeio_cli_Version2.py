import argparse
import logging
import sys
try:
    import yaml
except ImportError:  # pragma: no cover - fallback when PyYAML is missing
    yaml = None
try:
    from raeio_agent import RAEIOAgent
except Exception:  # pragma: no cover - minimal stub if dependencies missing
    class RAEIOAgent:  # type: ignore
        def __init__(self, config, logger):
            pass

        def run_task(self, task_type, prompt, context, plugin=None):
            return f"Stub output for {task_type}: {prompt}"


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


def main():
    parser = argparse.ArgumentParser(description="RAE.IO CLI")
    parser.add_argument(
        "--mode",
        choices=MODES,
        help="Operation mode",
        default=None,
    )
    parser.add_argument("--prompt", type=str, help="Prompt for generation/analysis")
    parser.add_argument("--url", type=str, help="URL for browser automation")
    parser.add_argument("--actions", type=str, help="Browser actions as JSON list")
    parser.add_argument("--plugin", type=str, help="Plugin name (optional)")
    args = parser.parse_args()

    if not args.mode:
        if sys.stdin.isatty():
            try:
                user_mode = input("Select mode [Text]: ").strip()
                args.mode = user_mode or "Text"
            except EOFError:
                args.mode = "Text"
        else:
            args.mode = "Text"

    if yaml:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    else:  # pragma: no cover
        config = {}
    logger = logging.getLogger("RAEIO_CLI")
    agent = RAEIOAgent(config, logger)

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
    print(f"Output:\n{output}")


if __name__ == "__main__":
    main()
