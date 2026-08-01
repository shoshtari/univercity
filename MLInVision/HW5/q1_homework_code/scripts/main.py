import argparse

from scripts.train import train
from scripts.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description="CREMA-D training and evaluation")
    subparsers = parser.add_subparsers(dest="command")

    train_parser = subparsers.add_parser("train", help="Run training loop")

    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a checkpoint")
    eval_parser.add_argument("--checkpoint", type=str, required=True)
    eval_parser.add_argument(
        "--split", type=str, default="test", choices=["train", "val", "test"]
    )

    args = parser.parse_args()

    if args.command == "train":
        train()
    elif args.command == "evaluate":
        evaluate(checkpoint=args.checkpoint, split=args.split)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
