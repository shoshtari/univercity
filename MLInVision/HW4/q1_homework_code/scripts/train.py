import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from models.model import _prepare_batch
from models.vocab import Vocab
from scripts.eval import eval

IGNORE_INDEX = -100


def _train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    vocab: Vocab,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    tag_key: str = "ner_tags",
) -> float:
    model.train()
    criterion = nn.CrossEntropyLoss(ignore_index=IGNORE_INDEX)
    total_loss = 0.0
    total_batches = 0

    for batch in dataloader:
        input_ids, labels, _ = _prepare_batch(batch, vocab, tag_key, device)
        optimizer.zero_grad()
        logits = model(input_ids)
        loss = criterion(logits.view(-1, logits.size(-1)), labels.view(-1))
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        total_batches += 1

    return total_loss / max(total_batches, 1)


def train(
    model: nn.Module,
    train_dl: DataLoader,
    val_dl: DataLoader,
    vocab: Vocab,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epochs: int,
    tag_key: str = "ner_tags",
    verbose: bool = True,
) -> list[dict[str, float]]:
    metadata: list[dict[str, float]] = []

    if verbose:
        train_loss, _ = eval(model, train_dl, vocab, device, tag_key)
        val_loss, val_acc = eval(model, val_dl, vocab, device, tag_key)
        print(
            f"Initial: "
            f"train_loss={train_loss:.4f} "
            f"val_loss={val_loss:.4f} "
            f"val_acc={val_acc:.4f} "
        )

    start_time = time.time()
    for epoch in range(epochs):
        train_loss = _train_one_epoch(
            model, train_dl, vocab, optimizer, device, tag_key
        )
        _, train_acc = eval(model, train_dl, vocab, device, tag_key)
        val_loss, val_acc = eval(model, val_dl, vocab, device, tag_key)
        metadata.append(
            {
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
            }
        )

        if verbose:
            print(
                f"epoch {epoch + 1}/{epochs}: "
                f"train_loss={train_loss:.4f} "
                f"val_loss={val_loss:.4f} "
                f"val_acc={val_acc:.4f}"
            )

    elapsed_time = time.time() - start_time
    print(f"Duration={elapsed_time:.2f}s")

    return metadata
