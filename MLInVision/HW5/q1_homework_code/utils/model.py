import os

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import AppConfig
from data.data_loader import CREMADDataset, collate_fn
from models.model import build_model
from utils.torch_device import get_device


def build_optimizer(model, cfg: AppConfig):
    name = cfg.training.optimizer.lower()
    lr = cfg.training.learning_rate
    if name == "adam":
        return torch.optim.Adam(model.parameters(), lr=lr)
    if name == "sgd":
        return torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    if name == "adamw":
        return torch.optim.AdamW(model.parameters(), lr=lr)
    raise ValueError(f"Unknown optimizer: {name!r}")


def build_criterion(cfg: AppConfig):
    name = cfg.training.loss_function.lower()
    if name in ("crossentropy", "cross_entropy", "ce"):
        return torch.nn.CrossEntropyLoss()
    if name == "mse":
        return torch.nn.MSELoss()
    raise ValueError(f"Unknown loss function: {name!r}")


def create_loaders(cfg: AppConfig):
    train_ds = CREMADDataset(split="train")
    val_ds = CREMADDataset(split="val")
    test_ds = CREMADDataset(split="test")

    bs = cfg.training.batch_size
    train_loader = DataLoader(
        train_ds, batch_size=bs, shuffle=True, num_workers=0, collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_ds, batch_size=bs, shuffle=False, num_workers=0, collate_fn=collate_fn
    )
    test_loader = DataLoader(
        test_ds, batch_size=bs, shuffle=False, num_workers=0, collate_fn=collate_fn
    )
    return train_loader, val_loader, test_loader


def save_checkpoint(
    model, cfg: AppConfig, epoch, val_acc, save_dir="models/saved_models"
):
    os.makedirs(save_dir, exist_ok=True)
    feat_name = cfg.feature.extractor
    ckpt_name = f"{feat_name}_best_acc={val_acc:.4f}.pt"
    ckpt_path = os.path.join(save_dir, ckpt_name)
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "val_acc": val_acc,
            "config": cfg,
        },
        ckpt_path,
    )
    return ckpt_path


def load_checkpoint(path, device):
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    return checkpoint


def run_epoch(model, loader, criterion, optimizer, device, training=True, epoch=0):
    model.train() if training else model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    ctx = torch.enable_grad() if training else torch.no_grad()
    with ctx:
        desc = "Training" if training else "Validation"
        if epoch:
            desc += f" (Epoch {epoch})"
        for batch in tqdm(loader, desc=desc):
            features = batch["features"].to(device)
            labels = batch["label"].to(device)

            if training:
                optimizer.zero_grad()

            outputs = model(features)
            loss = criterion(outputs, labels)

            if training:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * labels.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    avg_loss = total_loss / total
    acc = correct / total
    return avg_loss, acc
