
import argparse
import copy
import csv
import logging
import sys
import time
from pathlib import Path
from typing import Any, Mapping

import torch
import torch.nn.functional as functional
from torch import Tensor, nn
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.data_loader import (
    SuperResolutionDataset,
    build_validation_dataloader,
    generate_demo_dataset,
)
from models.model import build_model
from utils.config import configure_logging, load_config, save_json, select_device
from utils.metrics import MetricAccumulator, evaluate_pair
from utils.visualization import save_comparison

LOGGER = logging.getLogger(__name__)


def load_checkpoint(
    model: nn.Module, checkpoint_path: Path, device: torch.device
) -> dict[str, Any]:
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint does not exist: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    state = checkpoint.get("model_state", checkpoint)
    model.load_state_dict(state, strict=True)
    return checkpoint if isinstance(checkpoint, dict) else {"model_state": state}


@torch.inference_mode()
def evaluate_model(
    model: nn.Module,
    loader: DataLoader[Any],
    device: torch.device,
    scale: int,
    *,
    output_dir: Path | None = None,
    save_images: int = 1,
) -> dict[str, Any]:
    model.eval()
    model_metrics = MetricAccumulator()
    bicubic_metrics = MetricAccumulator()
    rows: list[dict[str, Any]] = []
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    for index, batch in enumerate(loader):
        lr = batch["lr"].to(device, non_blocking=True)
        target = batch["hr"].to(device, non_blocking=True)
        name_value = batch["name"]
        name = (
            name_value[0] if isinstance(name_value, (list, tuple)) else str(name_value)
        )

        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = time.perf_counter()
        prediction = model(lr).clamp(0.0, 1.0)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        bicubic = functional.interpolate(
            lr, scale_factor=scale, mode="bicubic", align_corners=False
        ).clamp(0.0, 1.0)
        if prediction.shape[-2:] != target.shape[-2:]:
            height = min(prediction.shape[-2], target.shape[-2])
            width = min(prediction.shape[-1], target.shape[-1])
            prediction = prediction[..., :height, :width]
            bicubic = bicubic[..., :height, :width]
            target = target[..., :height, :width]

        model_psnr, model_ssim = evaluate_pair(prediction, target, scale)
        bicubic_psnr, bicubic_ssim = evaluate_pair(bicubic, target, scale)
        model_metrics.update(model_psnr, model_ssim, elapsed_ms)
        bicubic_metrics.update(bicubic_psnr, bicubic_ssim)
        rows.append(
            {
                "image": name,
                "stsn_psnr": model_psnr,
                "stsn_ssim": model_ssim,
                "bicubic_psnr": bicubic_psnr,
                "bicubic_ssim": bicubic_ssim,
                "inference_ms": elapsed_ms,
            }
        )
        if output_dir is not None and index < save_images:
            save_comparison(
                lr[0],
                bicubic[0],
                prediction[0],
                target[0],
                output_dir / f"comparison_{name}.png",
            )

    result = {
        "stsn": model_metrics.averages(),
        "bicubic": bicubic_metrics.averages(),
        "per_image": rows,
    }
    if output_dir is not None:
        save_json(result, output_dir / "evaluation.json")
        if rows:
            with (output_dir / "per_image_metrics.csv").open(
                "w", newline="", encoding="utf-8-sig"
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    return result


def evaluate_checkpoint(
    config: Mapping[str, Any],
    project_root: Path,
    checkpoint_path: Path,
    *,
    quick: bool = False,
    device_name: str | None = None,
) -> dict[str, Any]:
    device = select_device(
        device_name or str(config.get("runtime", {}).get("device", "auto"))
    )
    model = build_model(config).to(device)
    load_checkpoint(model, checkpoint_path, device)
    if quick:
        generate_demo_dataset(project_root / "data" / "dataset")
    validation_loader = build_validation_dataloader(config, project_root, quick=quick)
    output_value = config.get("paths", {}).get("output_dir", "outputs")
    mode_name = "quick" if quick else f"x{config['model']['scale']}"
    output_dir = project_root / output_value / mode_name
    result = evaluate_model(
        model,
        validation_loader,
        device,
        int(config["model"]["scale"]),
        output_dir=output_dir,
        save_images=int(config.get("evaluation", {}).get("save_images", 1)),
    )
    LOGGER.info(
        "STSN: %.3f dB / %.4f SSIM", result["stsn"]["psnr"], result["stsn"]["ssim"]
    )
    LOGGER.info(
        "Bicubic: %.3f dB / %.4f SSIM",
        result["bicubic"]["psnr"],
        result["bicubic"]["ssim"],
    )
    return result


BENCHMARKS = {
    "Set5": ("Set5/GTmod12", "Set5/LRbicx{scale}"),
    "Set14": ("Set14/GTmod12", "Set14/LRbicx{scale}"),
    "B100": ("BSDS100", "BSDS100/LRbicx{scale}"),
    "Urban100": ("urban100", "urban100/LRbicx{scale}"),
    "Manga109": ("manga109", "manga109/LRbicx{scale}"),
}


def evaluate_benchmarks(
    config: Mapping[str, Any],
    project_root: Path,
    checkpoint_path: Path,
    *,
    device_name: str | None = None,
) -> dict[str, Any]:
    device = select_device(
        device_name or str(config.get("runtime", {}).get("device", "auto"))
    )
    scale = int(config["model"]["scale"])
    model = build_model(config).to(device)
    load_checkpoint(model, checkpoint_path, device)
    benchmark_value = config.get("paths", {}).get(
        "benchmark_root", "data/dataset/benchmarks"
    )
    benchmark_root = Path(benchmark_value)
    if not benchmark_root.is_absolute():
        benchmark_root = project_root / benchmark_root
    output_root = (
        project_root
        / config.get("paths", {}).get("output_dir", "outputs")
        / f"x{scale}"
        / "benchmarks"
    )
    results: dict[str, Any] = {}
    for name, (hr_template, lr_template) in BENCHMARKS.items():
        hr_dir = benchmark_root / hr_template.format(scale=scale)
        lr_dir = benchmark_root / lr_template.format(scale=scale)
        dataset = SuperResolutionDataset(hr_dir, scale, lr_dir=lr_dir, training=False)
        loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
        result = evaluate_model(
            model,
            loader,
            device,
            scale,
            output_dir=output_root / name,
            save_images=int(config.get("evaluation", {}).get("save_images", 1)),
        )
        results[name] = {
            key: value for key, value in result.items() if key != "per_image"
        }
        LOGGER.info(
            "x%d %s | STSN %.3f / %.4f | Bicubic %.3f / %.4f",
            scale,
            name,
            result["stsn"]["psnr"],
            result["stsn"]["ssim"],
            result["bicubic"]["psnr"],
            result["bicubic"]["ssim"],
        )
    summary = {"scale": scale, "checkpoint": str(checkpoint_path), "datasets": results}
    save_json(summary, output_root / "summary.json")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=PROJECT_ROOT / "config" / "config.yaml"
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Evaluate only the generated 4-image demo subset.",
    )
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    config = load_config(args.config)
    evaluate_checkpoint(
        config, PROJECT_ROOT, args.checkpoint, quick=args.quick, device_name=args.device
    )


if __name__ == "__main__":
    main()
