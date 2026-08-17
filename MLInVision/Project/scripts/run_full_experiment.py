
import argparse
import copy
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate import evaluate_benchmarks
from scripts.train import train_model
from utils.config import configure_logging, load_config, save_json

PATCH_SIZES = {2: 96, 3: 144, 4: 192}


def scale_config(base: dict, scale: int, epochs: int) -> dict:
    config = copy.deepcopy(base)
    config["model"]["scale"] = scale
    config["data"].update(
        {
            "train_hr_dir": "data/dataset/DIV2K/DIV2K_train_HR",
            "train_lr_dir": f"data/dataset/DIV2K/DIV2K_train_LR_bicubic/X{scale}",
            "val_hr_dir": "data/dataset/benchmarks/Set5/GTmod12",
            "val_lr_dir": f"data/dataset/benchmarks/Set5/LRbicx{scale}",
            "hr_patch_size": PATCH_SIZES[scale],
            "repeat": 1,
        }
    )
    config["training"].update(
        {"epochs": epochs, "batch_size": 32, "validation_interval": 10}
    )
    last_checkpoint = PROJECT_ROOT / "models" / "saved_models" / f"x{scale}" / "last.pt"
    if last_checkpoint.exists():
        config["training"]["resume_checkpoint"] = str(
            last_checkpoint.relative_to(PROJECT_ROOT)
        )
    else:
        config["training"]["resume_checkpoint"] = None
    return config


def warm_start_config(
    stage_one_config: dict,
    scale: int,
    epochs: int,
    pretrained_checkpoint: Path,
) -> dict:
    config = copy.deepcopy(stage_one_config)
    config["paths"]["saved_models_dir"] = "models/saved_models/warm_start"
    config["paths"]["output_dir"] = "outputs/warm_start"
    config["training"]["epochs"] = epochs
    config["training"]["warm_start_checkpoint"] = str(
        pretrained_checkpoint.relative_to(PROJECT_ROOT)
    )
    last_checkpoint = (
        PROJECT_ROOT
        / "models"
        / "saved_models"
        / "warm_start"
        / f"x{scale}"
        / "last.pt"
    )
    config["training"]["resume_checkpoint"] = (
        str(last_checkpoint.relative_to(PROJECT_ROOT))
        if last_checkpoint.exists()
        else None
    )
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=PROJECT_ROOT / "config" / "config.yaml"
    )
    parser.add_argument(
        "--scales", type=int, nargs="+", default=[2, 3, 4], choices=[2, 3, 4]
    )
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--device", default=None)
    parser.add_argument(
        "--skip-warm-start",
        action="store_true",
        help="Only run the first training stage and omit the paper's warm-start stage.",
    )
    args = parser.parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    base = load_config(args.config)
    summaries = {}
    for scale in args.scales:
        config = scale_config(base, scale, args.epochs)
        save_json(
            config, PROJECT_ROOT / "outputs" / f"x{scale}" / "resolved_config.json"
        )
        stage_one_training = train_model(config, PROJECT_ROOT, device_name=args.device)
        stage_one_evaluation = evaluate_benchmarks(
            config,
            PROJECT_ROOT,
            Path(stage_one_training["checkpoint"]),
            device_name=args.device,
        )
        summaries[f"x{scale}"] = {
            "stage_one": {
                "best_psnr_set5": stage_one_training["best_psnr"],
                "checkpoint": str(stage_one_training["checkpoint"]),
                "evaluation": stage_one_evaluation["datasets"],
            }
        }
        save_json(summaries, PROJECT_ROOT / "outputs" / "full_experiment_summary.json")
        if not args.skip_warm_start:
            warm_config = warm_start_config(
                config,
                scale,
                args.epochs,
                Path(stage_one_training["checkpoint"]),
            )
            save_json(
                warm_config,
                PROJECT_ROOT
                / "outputs"
                / "warm_start"
                / f"x{scale}"
                / "resolved_config.json",
            )
            warm_training = train_model(
                warm_config, PROJECT_ROOT, device_name=args.device
            )
            warm_evaluation = evaluate_benchmarks(
                warm_config,
                PROJECT_ROOT,
                Path(warm_training["checkpoint"]),
                device_name=args.device,
            )
            summaries[f"x{scale}"]["warm_start"] = {
                "best_psnr_set5": warm_training["best_psnr"],
                "checkpoint": str(warm_training["checkpoint"]),
                "evaluation": warm_evaluation["datasets"],
            }
        save_json(summaries, PROJECT_ROOT / "outputs" / "full_experiment_summary.json")
    print(json.dumps(summaries, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
