
import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.data_loader import generate_demo_dataset
from scripts.evaluate import evaluate_checkpoint
from scripts.train import train_model
from utils.config import configure_logging, load_config
from utils.visualization import draw_architecture

LOGGER = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=PROJECT_ROOT / "config" / "config.yaml"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run the complete pipeline on a tiny local dataset.",
    )
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--max-batches", type=int, default=None)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    config = load_config(args.config)
    if args.quick:
        train_dir, val_dir = generate_demo_dataset(PROJECT_ROOT / "data" / "dataset")
        LOGGER.info("Quick dataset is ready: %s and %s", train_dir, val_dir)
    architecture_path = (
        PROJECT_ROOT
        / config.get("paths", {}).get("output_dir", "outputs")
        / "architecture.png"
    )
    draw_architecture(
        architecture_path,
        groups=int(config["model"]["num_groups"]),
        blocks_per_group=int(config["model"]["blocks_per_group"]),
    )

    checkpoint = args.checkpoint
    training_result = None
    if not args.skip_train:
        training_result = train_model(
            config,
            PROJECT_ROOT,
            quick=args.quick,
            epochs_override=args.epochs,
            max_batches_override=args.max_batches,
            device_name=args.device,
        )
        checkpoint = Path(training_result["checkpoint"])
    if checkpoint is None:
        raise ValueError("--checkpoint is required when --skip-train is used.")

    evaluation = evaluate_checkpoint(
        config,
        PROJECT_ROOT,
        checkpoint,
        quick=args.quick,
        device_name=args.device,
    )
    summary = {
        "mode": "quick" if args.quick else "full",
        "checkpoint": str(
            checkpoint.relative_to(PROJECT_ROOT)
            if checkpoint.is_relative_to(PROJECT_ROOT)
            else checkpoint
        ),
        "training": training_result,
        "evaluation": {
            key: value for key, value in evaluation.items() if key != "per_image"
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
