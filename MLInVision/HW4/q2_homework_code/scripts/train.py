import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from scripts.eval import evaluate


def train(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epochs: int,
) -> list[dict[str, float]]:
    metadata: list[dict[str, float]] = []

    print(f"\n--- Starting Training loop ({epochs} epochs) ---")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        start_time = time.time()

        for _, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)

            # Standard PyTorch Training Steps
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            # if (batch_idx + 1) % 100 == 0 or (batch_idx + 1) == len(train_loader):
            #     print(f"Epoch [{epoch+1}/{epochs}] | Batch [{batch_idx+1}/{len(train_loader)}] | Loss: {loss.item():.4f}")

        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = (correct / total) * 100
        eclapsed = time.time() - start_time

        val_loss, val_acc = evaluate(model, test_loader, device, criterion)
        metadata.append(
            {
                "train_loss": epoch_loss,
                "train_acc": epoch_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
            }
        )

        print(
            f"Epoch {epoch+1} "
            f"Train Loss: {epoch_loss:.4f} "
            f"Train Acc: {epoch_acc:.2f}% "
            f"Val Loss: {epoch_loss:.4f} "
            f"Val Acc: {epoch_acc:.2f}% "
            f"Duration: {eclapsed:.1f}s"
        )
    return metadata
