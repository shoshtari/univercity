from pathlib import Path
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
import yaml

from data.dataset import train_dataset, val_dataset, test_dataset
from data.data_loader import get_dataloader
from models.model import ViT
from scripts.eval import evaluate
from scripts.train import train
from utils.visualization import plot_training_summary

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)



def main(config_path: Path | str = DEFAULT_CONFIG_PATH) -> None:
    config = load_config(config_path)
    model_cfg = config["model"]
    train_cfg = config["training"]

    device = torch.device("cpu")
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    print(f"Targeting Device: {device}")

    train_loader = get_dataloader(train_dataset, batch_size=train_cfg["batch_size"])
    val_loader = get_dataloader(val_dataset, batch_size=train_cfg["batch_size"], shuffle=False)
    test_loader = get_dataloader(test_dataset, batch_size=train_cfg["batch_size"], shuffle=False)

    model = ViT(
        image_size=model_cfg["image_size"],
        patch_size=model_cfg["patch_size"],
        embedding_dim=model_cfg["embedding_dim"],
        num_heads=model_cfg["num_heads"],
        num_layers=model_cfg["num_layers"],
        num_classes=model_cfg["num_classes"],
        mlp_hidden_dim=model_cfg.get("mlp_hidden_dim"),
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=train_cfg["lr"],
        weight_decay=train_cfg["weight_decay"],
    )

    metadata = train(
        model,
        train_loader,
        val_loader,
        optimizer,
        criterion,
        device,
        epochs=train_cfg["epochs"],
    )

    print("\nFinal evaluation on test set:")
    evaluate(model, test_loader, device, criterion)

    viz_cfg = config.get("visualization", {})
    if viz_cfg.get("enabled", False):

        fig = plot_training_summary(metadata, model_name="ViT")
        save_path = viz_cfg.get("save_path")
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Saved training plots to {save_path}")
        else:
            plt.show()


if __name__ == "__main__":
    main()
