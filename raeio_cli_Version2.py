import argparse
import yaml
import logging
from raeio_agent import RAEIOAgent


def main():
    parser = argparse.ArgumentParser(description="RAE.IO CLI")
    parser.add_argument('--mode', choices=['Art', 'Sound', 'Video', 'Text', 'TCG', 'Fuckery', 'Training', 'Browser'],
                        help='Run an agent task in the specified mode')
    parser.add_argument('--prompt', type=str, help='Prompt for generation/analysis')
    parser.add_argument('--url', type=str, help='URL for browser automation')
    parser.add_argument('--actions', type=str, help='Browser actions as JSON list')
    parser.add_argument('--plugin', type=str, help='Plugin name (optional)')

    parser.add_argument('--train-model', choices=['llama', 'sd'],
                        help='Fine-tune the specified model on a dataset')
    parser.add_argument('--dataset', type=str, help='Path to training dataset')
    parser.add_argument('--restore-model', choices=['llama', 'sd'],
                        help='Restore a model from a checkpoint')
    parser.add_argument('--checkpoint', type=str, help='Checkpoint version to restore')

    args = parser.parse_args()

    if args.train_model:
        if not args.dataset:
            print("Provide --dataset to train a model.")
            return
        if args.train_model == 'llama':
            from trainers.llama_trainer import train_model
        else:
            from trainers.sd_trainer import train_model
        ckpt = train_model(args.dataset)
        print(f'Training complete. Checkpoint saved to {ckpt}')
        return

    if args.restore_model:
        if not args.checkpoint:
            print("Provide --checkpoint to restore a model.")
            return
        if args.restore_model == 'llama':
            from trainers.llama_trainer import restore_checkpoint
        else:
            from trainers.sd_trainer import restore_checkpoint
        metadata = restore_checkpoint(args.checkpoint)
        print(f'Restored {args.restore_model} checkpoint {args.checkpoint}: {metadata}')
        return

    if not args.mode:
        parser.error("Either --mode or training/restore options must be provided.")

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
    else:
        context = {}
        output = agent.run_task(args.mode.lower(), args.prompt or "", context, plugin=args.plugin)
    print(f"Output:\n{output}")


if __name__ == "__main__":
    main()
