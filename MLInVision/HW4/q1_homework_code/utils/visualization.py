from __future__ import annotations
from typing import Mapping, Sequence
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from collections.abc import Mapping, Sequence

import matplotlib.pyplot as plt


def _metric_values(metadata: Sequence[Mapping[str, float]], key: str) -> list[float]:
    return [float(item.get(key, float("nan"))) for item in metadata]


def _report_rows(report: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    class_support = 0

    for label, values in report.items():
        if label in {"macro avg", "weighted avg"}:
            continue
        if label == "accuracy":
            rows.append(
                ["accuracy", "", "", f"{float(values):.4f}", str(class_support)]
            )
            continue

        if not isinstance(values, Mapping):
            continue

        precision = float(values.get("precision", float("nan")))
        recall = float(values.get("recall", float("nan")))
        f1_score = float(values.get("f1-score", float("nan")))
        support = int(values.get("support", 0))
        class_support += support
        rows.append(
            [
                str(label),
                f"{precision:.4f}",
                f"{recall:.4f}",
                f"{f1_score:.4f}",
                str(support),
            ]
        )

    for label in ("macro avg", "weighted avg"):
        values = report.get(label)
        if isinstance(values, Mapping):
            rows.append(
                [
                    label,
                    f"{float(values.get('precision', float('nan'))):.4f}",
                    f"{float(values.get('recall', float('nan'))):.4f}",
                    f"{float(values.get('f1-score', float('nan'))):.4f}",
                    str(int(values.get("support", class_support))),
                ]
            )

    return rows


def plot_training_summary(
    metadata: Sequence[Mapping[str, float]],
    report: dict[str, object],
    model_name: str,
):
    epochs = list(range(1, len(metadata) + 1))
    train_loss = _metric_values(metadata, "train_loss")
    val_loss = _metric_values(metadata, "val_loss")
    train_acc = _metric_values(metadata, "train_acc")
    val_acc = _metric_values(metadata, "val_acc")

    fig = plt.figure(figsize=(18, 10), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 1.25])

    loss_ax = fig.add_subplot(grid[0, 0])
    acc_ax = fig.add_subplot(grid[0, 1])
    report_ax = fig.add_subplot(grid[1, :])

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
    acc_ax.set_ylabel("Accuracy")
    acc_ax.grid(True, alpha=0.3)
    acc_ax.legend(frameon=False)

    report_ax.axis("off")
    report_rows = _report_rows(report)
    table = report_ax.table(
        cellText=report_rows,
        colLabels=["Class", "Precision", "Recall", "F1", "Support"],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)

    cmap = plt.cm.YlGn
    norm = mcolors.Normalize(vmin=0.0, vmax=1.0)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.set_linewidth(1.5)

        if row == 0:
            cell.set_facecolor("#2c3e50")  # Dark modern header
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
            continue

        if col in (0, 4):
            cell.set_facecolor("#f8f9fa")
            if col == 0:
                cell.get_text().set_weight("bold")
            continue

        cell_text = cell.get_text().get_text().strip()
        if not cell_text:
            continue
        val = float(cell_text)
        color = cmap(norm(val))
        cell.set_facecolor(color)

        if val > 0.75:
            cell.get_text().set_color("white")
        else:
            cell.get_text().set_color("black")

    report_ax.set_title("Classification Report", pad=18, fontsize=14)

    fig.suptitle(model_name, fontsize=16)

    return fig
