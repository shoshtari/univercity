
import csv
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.config import save_json

DATASETS = ("Set5", "Set14", "B100", "Urban100", "Manga109")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a JSON object in {path}.")
    return payload


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        raise ValueError("At least one row is required to write a CSV file.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def collect() -> dict[str, Any]:
    scales: dict[str, Any] = {}
    training_rows: list[dict[str, Any]] = []
    benchmark_rows: list[dict[str, Any]] = []
    for scale in (2, 3, 4):
        stage_one = load_json(
            PROJECT_ROOT / "outputs" / f"x{scale}" / "kaggle_run_summary.json"
        )
        warm_start = load_json(
            PROJECT_ROOT
            / "outputs"
            / "warm_start"
            / f"x{scale}"
            / "kaggle_run_summary.json"
        )
        for label, result in (("stage_one", stage_one), ("warm_start", warm_start)):
            run = result["run"]
            if int(run["scale"]) != scale:
                raise ValueError(f"Scale mismatch in {label} x{scale} output.")
            if int(run["train_images"]) != 800 or int(run["lr_images"]) != 800:
                raise ValueError(f"Incomplete DIV2K input in {label} x{scale} output.")
            if int(result["training"]["completed_epochs"]) != 100:
                raise ValueError(f"Incomplete training in {label} x{scale} output.")
            training_rows.append(
                {
                    "scale": scale,
                    "stage": label,
                    "parameters": int(run["parameters"]),
                    "epochs": int(run["epochs"]),
                    "train_images": int(run["train_images"]),
                    "training_seconds": float(result["training"]["training_seconds"]),
                    "wall_seconds": float(result["wall_seconds"]),
                    "gpu": run["gpu"],
                    "torch": run["torch"],
                    "cuda": run["cuda"],
                }
            )
            for dataset in DATASETS:
                metrics = result["evaluation"]["datasets"][dataset]
                benchmark_rows.append(
                    {
                        "scale": scale,
                        "stage": label,
                        "dataset": dataset,
                        "image_count": int(metrics["stsn"]["count"]),
                        "stsn_psnr": float(metrics["stsn"]["psnr"]),
                        "stsn_ssim": float(metrics["stsn"]["ssim"]),
                        "bicubic_psnr": float(metrics["bicubic"]["psnr"]),
                        "bicubic_ssim": float(metrics["bicubic"]["ssim"]),
                        "stsn_time_ms": float(metrics["stsn"]["time_ms"]),
                    }
                )
        scales[f"x{scale}"] = {"stage_one": stage_one, "warm_start": warm_start}

    output = {
        "protocol": {
            "scales": [2, 3, 4],
            "stage_one_epochs": 100,
            "warm_start_epochs": 100,
            "train_images_per_stage": 800,
            "final_weight_policy": "last epoch of each fixed-budget stage",
        },
        "scales": scales,
    }
    save_json(output, PROJECT_ROOT / "outputs" / "full_experiment_summary.json")
    write_csv(training_rows, PROJECT_ROOT / "outputs" / "training_summary.csv")
    write_csv(benchmark_rows, PROJECT_ROOT / "outputs" / "full_benchmark_results.csv")
    return output


def main() -> None:
    collect()
    print(PROJECT_ROOT / "outputs" / "full_experiment_summary.json")
    print(PROJECT_ROOT / "outputs" / "training_summary.csv")
    print(PROJECT_ROOT / "outputs" / "full_benchmark_results.csv")


if __name__ == "__main__":
    main()
