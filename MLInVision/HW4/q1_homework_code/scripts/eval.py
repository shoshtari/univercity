import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from models.model import _prepare_batch
from models.vocab import Vocab

IGNORE_INDEX = -100


@torch.no_grad()
def eval(
    model: nn.Module,
    dataloader: DataLoader,
    vocab: Vocab,
    device: torch.device,
    tag_key: str = "ner_tags",
) -> tuple[float, float]:
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=IGNORE_INDEX)
    total_loss = 0.0
    total_batches = 0
    correct = 0
    total = 0

    for batch in dataloader:
        input_ids, labels, _ = _prepare_batch(batch, vocab, tag_key, device)
        logits = model(input_ids)
        loss = criterion(
            logits.view(-1, logits.size(-1)), 
            labels.view(-1)
        )

        total_loss += loss.item()
        total_batches += 1

        preds = logits.argmax(dim=-1)
        mask = labels != IGNORE_INDEX
        correct += (preds[mask] == labels[mask]).sum().item()
        total += mask.sum().item()

    avg_loss = total_loss / max(total_batches, 1)
    accuracy = correct / max(total, 1)
    return avg_loss, accuracy


@torch.no_grad()
def collect_predictions(
    model: nn.Module,
    dataloader: DataLoader,
    vocab: Vocab,
    device: torch.device,
    tag_key: str = "ner_tags",
) -> tuple[list[int], list[int]]:
    model.eval()
    y_true: list[int] = []
    y_pred: list[int] = []

    for batch in dataloader:
        input_ids, labels, _ = _prepare_batch(batch, vocab, tag_key, device)
        logits = model(input_ids)
        preds = logits.argmax(dim=-1)
        mask = labels != IGNORE_INDEX
        y_true.extend(labels[mask].tolist())
        y_pred.extend(preds[mask].tolist())

    return y_true, y_pred
