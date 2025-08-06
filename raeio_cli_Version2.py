import argparse
import yaml
import logging
from raeio_agent import RAEIOAgent
from model_trainer import train_model

def main():
    parser = argparse.ArgumentParser(description="RAE.IO CLI")
    parser.add_argument('--mode', choices=['Art', 'Sound', 'Video', 'Text', 'TCG', 'Fuckery', 'Training', 'Browser'], required=True)
    parser.add_argument('--prompt', type=str, help='Prompt for generation/analysis')
    parser.add_argument('--url', type=str, help='URL for browser automation')
    parser.add_argument('--actions', type=str, help='Browser actions as JSON list')
    parser.add_argument('--plugin', type=str, help='Plugin name (optional)')
    parser.add_argument('--model', choices=['sd', 'llama'], help='Model to train when using Training mode')
    parser.add_argument('--dataset', type=str, help='Path to local dataset for training')
    parser.add_argument('--output', type=str, default='checkpoints', help='Directory for saving checkpoints')
    args = parser.parse_args()

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
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
        print(f"Output:\n{output}")
        return

    if args.mode == "Training":
        if not args.model or not args.dataset:
            print("Training mode requires --model and --dataset")
            return
        result = train_model(args.model, args.dataset, args.output)
        print(f"Training complete. Checkpoint saved to {result['checkpoint']}")
        return

    context = {}
    output = agent.run_task(args.mode.lower(), args.prompt or "", context, plugin=args.plugin)
    print(f"Output:\n{output}")

if __name__ == "__main__":
    main()