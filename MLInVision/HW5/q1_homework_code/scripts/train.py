import glob
import json
import os
import time
from dataclasses import asdict

import torch
from tqdm import tqdm

from config import config
from utils.model import (
    build_criterion,
    build_model,
    build_optimizer,
    create_loaders,
    get_device,
    run_epoch,
    save_checkpoint,
)


def train():
    device = get_device()
    train_loader, val_loader, test_loader = create_loaders(config)

    model = build_model(config).to(device)
    optimizer = build_optimizer(model, config)
    criterion = build_criterion(config)

    print(f"Device       : {device}")
    print(
        f"Model params : {sum(p.numel() for p in model.parameters() if p.requires_grad):,}"
    )
    print(f"Train samples: {len(train_loader.dataset)}")
    print(f"Val samples  : {len(val_loader.dataset)}")
    print(f"Feature      : {config.feature.extractor}")
    print()

    best_val_acc = 0.0
    save_dir = os.path.join("models", "saved_models")
    os.makedirs(save_dir, exist_ok=True)

    epochs = config.training.epochs
    history: list[dict] = []

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss, train_acc = run_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
            training=True,
            epoch=epoch,
        )
        val_loss, val_acc = run_epoch(
            model, val_loader, criterion, None, device, training=False, epoch=epoch
        )
        elapsed = time.time() - t0

        tqdm.write(
            f"Epoch {epoch:3d}/{epochs}  "
            f"[{elapsed:.1f}s]  "
            f"train_loss={train_loss:.4f}  train_acc={train_acc:.4f}  "
            f"val_loss={val_loss:.4f}  val_acc={val_acc:.4f}"
        )

        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "time_sec": elapsed,
            }
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_checkpoint(model, config, epoch, best_val_acc, save_dir)

    extractor_name = config.feature.extractor
    history_path = os.path.join(save_dir, f"history_{extractor_name}.json")
    with open(history_path, "w") as f:
        json.dump({"history": history, "config": asdict(config)}, f, indent=2)
    print(f"\nHistory saved to: {history_path}")

    print(f"\nBest val acc: {best_val_acc:.4f}")
    _evaluate_on_test(model, test_loader, criterion, device, save_dir, config)


def _evaluate_on_test(model, test_loader, criterion, device, save_dir, cfg):
    checkpoints = sorted(
        glob.glob(os.path.join(save_dir, f"{cfg.feature.extractor}_best_acc=*.pt"))
    )
    if not checkpoints:
        print("No checkpoint found for test evaluation.")
        return

    best_ckpt = max(
        checkpoints, key=lambda p: float(p.split("best_acc=")[-1].replace(".pt", ""))
    )
    print(f"Loading best checkpoint: {best_ckpt}")
    ckpt = torch.load(best_ckpt, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])

    test_loss, test_acc = run_epoch(
        model, test_loader, criterion, None, device, training=False
    )
    print(f"Test  loss={test_loss:.4f}  test_acc={test_acc:.4f}")

    results_path = os.path.join(save_dir, f"{cfg.feature.extractor}_results.json")
    result = {
        "val_acc": ckpt["val_acc"],
        "test_acc": test_acc,
        "test_loss": test_loss,
        "epoch": ckpt["epoch"],
        "checkpoint": best_ckpt,
        "config": cfg,
    }
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Results saved to: {results_path}")
