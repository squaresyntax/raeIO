import argparse
import yaml
import logging
from raeio_agent import RAEIOAgent

def main():
    parser = argparse.ArgumentParser(description="RAE.IO CLI")
    parser.add_argument('--mode', choices=['Art', 'Sound', 'Video', 'Text', 'TCG', 'Fuckery', 'Training', 'Browser'], required=True)
    parser.add_argument('--prompt', type=str, help='Prompt for generation/analysis')
    parser.add_argument('--url', type=str, help='URL for browser automation')
    parser.add_argument('--actions', type=str, help='Browser actions as JSON list')
    parser.add_argument('--plugin', type=str, help='Plugin name (optional)')
    parser.add_argument('--enable-feature', action='append', default=[],
                        help='Enable a feature (can be used multiple times)')
    parser.add_argument('--disable-feature', action='append', default=[],
                        help='Disable a feature (can be used multiple times)')
    args = parser.parse_args()

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    features = config.setdefault("features", {})
    for name in args.enable_feature:
        features[name] = True
    for name in args.disable_feature:
        features[name] = False
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
        output = agent.run_task(args.mode.lower(), args.prompt or "", context, plugin=args.plugin)
    print(f"Output:\n{output}")

if __name__ == "__main__":
    main()
