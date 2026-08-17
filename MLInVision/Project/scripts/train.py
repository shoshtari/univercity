
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any, Mapping

import torch
from torch import nn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.data_loader import build_dataloaders, generate_demo_dataset
from models.model import build_model, count_parameters
from scripts.evaluate import evaluate_model, load_checkpoint
from utils.config import (
    configure_logging,
    load_config,
    save_json,
    select_device,
    set_seed,
)
from utils.visualization import plot_training_history

LOGGER = logging.getLogger(__name__)


def _checkpoint_payload(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    epoch: int,
    history: list[dict[str, float]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "scheduler_state": scheduler.state_dict(),
        "history": history,
        "config": dict(config),
    }


def _save_checkpoint(payload: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(dict(payload), temporary)
    temporary.replace(path)


def train_model(
    config: Mapping[str, Any],
    project_root: Path,
    *,
    quick: bool = False,
    epochs_override: int | None = None,
    max_batches_override: int | None = None,
    device_name: str | None = None,
) -> dict[str, Any]:
    runtime_cfg = config.get("runtime", {})
    training_cfg = config.get("training", {})
    quick_cfg = config.get("quick", {}) if quick else {}
    seed = int(runtime_cfg.get("seed", 810104039))
    set_seed(seed, bool(runtime_cfg.get("deterministic", True)))
    device = select_device(device_name or str(runtime_cfg.get("device", "auto")))
    if quick:
        generate_demo_dataset(project_root / "data" / "dataset")
    train_loader, validation_loader = build_dataloaders(
        config, project_root, quick=quick
    )
    model = build_model(config).to(device)
    LOGGER.info(
        "Device: %s | trainable parameters: %s", device, f"{count_parameters(model):,}"
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(training_cfg.get("learning_rate", 5e-4)),
        betas=(
            float(training_cfg.get("beta1", 0.9)),
            float(training_cfg.get("beta2", 0.99)),
        ),
        eps=float(training_cfg.get("epsilon", 1e-8)),
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=int(training_cfg.get("lr_step_epochs", 200)),
        gamma=float(training_cfg.get("lr_gamma", 0.5)),
    )
    criterion = nn.L1Loss()

    warm_start_value = training_cfg.get("warm_start_checkpoint")
    if warm_start_value:
        warm_start_path = Path(warm_start_value)
        if not warm_start_path.is_absolute():
            warm_start_path = project_root / warm_start_path
        load_checkpoint(model, warm_start_path, device)
        LOGGER.info(
            "Warm start from %s (optimizer is intentionally reset).", warm_start_path
        )

    epochs = int(
        epochs_override or quick_cfg.get("epochs", training_cfg.get("epochs", 1000))
    )
    max_batches = max_batches_override
    if max_batches is None:
        max_batches = quick_cfg.get("max_batches_per_epoch")
    output_root = project_root / config.get("paths", {}).get(
        "saved_models_dir", "models/saved_models"
    )
    run_dir = output_root / ("quick" if quick else f"x{config['model']['scale']}")
    mode_name = "quick" if quick else f"x{config['model']['scale']}"
    output_dir = (
        project_root / config.get("paths", {}).get("output_dir", "outputs") / mode_name
    )
    history: list[dict[str, float]] = []
    best_psnr = float("-inf")
    best_path = run_dir / "best.pt"
    last_path = run_dir / "last.pt"
    log_interval = int(training_cfg.get("log_interval", 10))
    start_epoch = 1

    resume_value = training_cfg.get("resume_checkpoint")
    if resume_value:
        resume_path = Path(resume_value)
        if not resume_path.is_absolute():
            resume_path = project_root / resume_path
        checkpoint = load_checkpoint(model, resume_path, device)
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        scheduler.load_state_dict(checkpoint["scheduler_state"])
        history = list(checkpoint.get("history", []))
        start_epoch = int(checkpoint.get("epoch", 0)) + 1
        if history:
            best_psnr = max(
                float(item.get("val_psnr", float("-inf"))) for item in history
            )
        LOGGER.info("Resume training from epoch %d using %s", start_epoch, resume_path)

    if start_epoch > epochs:
        LOGGER.info("Requested %d epochs are already complete.", epochs)
        final_path = last_path if last_path.exists() else best_path
        return {
            "checkpoint": final_path,
            "best_checkpoint": best_path,
            "history": history,
            "best_psnr": best_psnr,
            "device": str(device),
        }

    validation_interval = int(training_cfg.get("validation_interval", 1))
    for epoch in range(start_epoch, epochs + 1):
        epoch_start = time.perf_counter()
        model.train()
        total_loss = 0.0
        processed = 0
        for batch_index, batch in enumerate(train_loader, start=1):
            if max_batches is not None and batch_index > int(max_batches):
                break
            lr = batch["lr"].to(device, non_blocking=True)
            target = batch["hr"].to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            prediction = model(lr)
            loss = criterion(prediction, target)
            loss.backward()
            clip_value = training_cfg.get("gradient_clip")
            if clip_value is not None:
                nn.utils.clip_grad_norm_(model.parameters(), float(clip_value))
            optimizer.step()
            total_loss += loss.item()
            processed += 1
            if batch_index % log_interval == 0:
                LOGGER.info(
                    "epoch %d/%d | batch %d | L1 %.6f",
                    epoch,
                    epochs,
                    batch_index,
                    loss.item(),
                )
        if processed == 0:
            raise RuntimeError("No training batches were processed.")

        should_validate = epoch % validation_interval == 0 or epoch == epochs
        validation = (
            evaluate_model(
                model,
                validation_loader,
                device,
                int(config["model"]["scale"]),
                output_dir=None,
                save_images=0,
            )
            if should_validate
            else {"stsn": {"psnr": float("nan"), "ssim": float("nan")}}
        )
        record = {
            "epoch": float(epoch),
            "train_l1": total_loss / processed,
            "val_psnr": float(validation["stsn"]["psnr"]),
            "val_ssim": float(validation["stsn"]["ssim"]),
            "learning_rate": float(optimizer.param_groups[0]["lr"]),
            "seconds": float(time.perf_counter() - epoch_start),
        }
        history.append(record)
        scheduler.step()
        payload = _checkpoint_payload(
            model, optimizer, scheduler, epoch, history, config
        )
        _save_checkpoint(payload, last_path)
        if should_validate and record["val_psnr"] >= best_psnr:
            best_psnr = record["val_psnr"]
            _save_checkpoint(payload, best_path)
        save_json(
            {"history": history, "best_psnr": best_psnr},
            output_dir / "training_history.json",
        )
        plot_training_history(history, output_dir / "training_curve.png")
        LOGGER.info(
            "epoch %d/%d | L1 %.6f | validation %.3f dB / %.4f | %.1f s",
            epoch,
            epochs,
            record["train_l1"],
            record["val_psnr"],
            record["val_ssim"],
            record["seconds"],
        )

    return {
        "checkpoint": last_path,
        "best_checkpoint": best_path,
        "history": history,
        "best_psnr": best_psnr,
        "device": str(device),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=PROJECT_ROOT / "config" / "config.yaml"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Train on the generated 8-image demo subset (and validate on 4 images).",
    )
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--max-batches", type=int, default=None)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    configure_logging(PROJECT_ROOT / "config" / "logging.yaml")
    config = load_config(args.config)
    train_model(
        config,
        PROJECT_ROOT,
        quick=args.quick,
        epochs_override=args.epochs,
        max_batches_override=args.max_batches,
        device_name=args.device,
    )


if __name__ == "__main__":
    main()
