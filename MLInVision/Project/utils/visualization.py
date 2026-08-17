
from pathlib import Path
from typing import Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from torch import Tensor

from data.data_loader import tensor_to_image


def plot_training_history(history: Sequence[Mapping[str, float]], path: Path) -> None:
    if not history:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    epochs = [int(item["epoch"]) for item in history]
    losses = [float(item["train_l1"]) for item in history]
    psnr_values = [float(item.get("val_psnr", float("nan"))) for item in history]
    figure, first_axis = plt.subplots(figsize=(7.2, 4.2))
    first_axis.plot(epochs, losses, marker="o", color="#1f77b4", label="Training L1")
    first_axis.set_xlabel("Epoch")
    first_axis.set_ylabel("L1 loss", color="#1f77b4")
    first_axis.grid(alpha=0.25)
    second_axis = first_axis.twinx()
    second_axis.plot(
        epochs, psnr_values, marker="s", color="#d62728", label="Validation PSNR"
    )
    second_axis.set_ylabel("PSNR (dB)", color="#d62728")
    figure.tight_layout()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def save_comparison(
    lr: Tensor, bicubic: Tensor, prediction: Tensor, target: Tensor, path: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    items = [
        (lr, "Low resolution"),
        (bicubic, "Bicubic"),
        (prediction, "STSN"),
        (target, "Reference HR"),
    ]
    figure, axes = plt.subplots(1, 4, figsize=(12, 3.2))
    for axis, (tensor, title) in zip(axes, items):
        axis.imshow(tensor_to_image(tensor))
        axis.set_title(title)
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def draw_architecture(path: Path, groups: int = 4, blocks_per_group: int = 4) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = [
        "LR image",
        "3x3 shallow\nconvolution",
        f"{groups} modulation groups\n({blocks_per_group} blocks each)",
        "Concatenate +\n1x1 and 3x3",
        "Global residual\naddition",
        "3x3 + PixelShuffle",
        "SR image",
    ]
    colors = [
        "#e8f1fb",
        "#d9ead3",
        "#fce5cd",
        "#fff2cc",
        "#ead1dc",
        "#d9d2e9",
        "#cfe2f3",
    ]
    figure, axis = plt.subplots(figsize=(13, 2.8))
    axis.set_xlim(0, len(labels) * 2.0)
    axis.set_ylim(0, 2.5)
    axis.axis("off")
    for index, (label, color) in enumerate(zip(labels, colors)):
        x_position = 0.25 + index * 2.0
        box = FancyBboxPatch(
            (x_position, 0.75),
            1.55,
            1.0,
            boxstyle="round,pad=0.04",
            facecolor=color,
            edgecolor="#444444",
            linewidth=1.2,
        )
        axis.add_patch(box)
        axis.text(x_position + 0.775, 1.25, label, ha="center", va="center", fontsize=9)
        if index < len(labels) - 1:
            axis.add_patch(
                FancyArrowPatch(
                    (x_position + 1.55, 1.25),
                    (x_position + 1.98, 1.25),
                    arrowstyle="->",
                    mutation_scale=13,
                    color="#333333",
                )
            )
    figure.tight_layout()
    figure.savefig(path, dpi=180, bbox_inches="tight", transparent=False)
    plt.close(figure)
