import torch

from config import AppConfig, config
from data.data_loader import CREMADDataset
from models.model import build_model
from utils.model import (
    build_criterion,
    collate_fn,
    get_device,
    load_checkpoint,
    run_epoch,
)


def evaluate(checkpoint: str, split: str = "test"):
    device = get_device()

    model = build_model(config).to(device)
    ckpt = load_checkpoint(checkpoint, device)
    model.load_state_dict(ckpt["model_state_dict"])

    ds = CREMADDataset(split=split)
    bs = config.training.batch_size
    loader = torch.utils.data.DataLoader(
        ds, batch_size=bs, shuffle=False, num_workers=0, collate_fn=collate_fn
    )
    criterion = build_criterion(config)

    loss, acc = run_epoch(model, loader, criterion, None, device, training=False)
    print(f"[{split}] loss={loss:.4f}  acc={acc:.4f}")
