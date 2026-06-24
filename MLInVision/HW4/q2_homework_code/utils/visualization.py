from __future__ import annotations

from collections.abc import Mapping, Sequence

import matplotlib.pyplot as plt


def _metric_values(metadata: Sequence[Mapping[str, float]], key: str) -> list[float]:
    return [float(item.get(key, float("nan"))) for item in metadata]


def plot_training_summary(
    metadata: Sequence[Mapping[str, float]],
    model_name: str = "ViT",
):
    """Plot train/val loss and accuracy curves over epochs."""
    epochs = list(range(1, len(metadata) + 1))
    train_loss = _metric_values(metadata, "train_loss")
    val_loss = _metric_values(metadata, "val_loss")
    train_acc = _metric_values(metadata, "train_acc")
    val_acc = _metric_values(metadata, "val_acc")

    fig, (loss_ax, acc_ax) = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    loss_ax.plot(epochs, train_loss, marker="o", label="train")
    loss_ax.plot(epochs, val_loss, marker="o", label="val")
    loss_ax.set_title("Loss")
    loss_ax.set_xlabel("Epoch")
    loss_ax.set_ylabel("Loss")
    loss_ax.grid(True, alpha=0.3)
    loss_ax.legend(frameon=False)

    acc_ax.plot(epochs, train_acc, marker="o", label="train")
    acc_ax.plot(epochs, val_acc, marker="o", label="val")
    acc_ax.set_title("Accuracy")
    acc_ax.set_xlabel("Epoch")
    acc_ax.set_ylabel("Accuracy (%)")
    acc_ax.grid(True, alpha=0.3)
    acc_ax.legend(frameon=False)

    fig.suptitle(model_name, fontsize=16)

    return fig
