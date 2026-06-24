from pathlib import Path

import torch
import torch.nn as nn
import yaml
from sklearn.metrics import classification_report
from torch.utils.data import DataLoader

from data.dataset import Conll2003Dataset
from data.dataloader import get_dataloader
from models.model import BiGRUTagger, BiLSTMTagger, BiRNNTagger
from models.vocab import Vocab
from scripts.eval import collect_predictions
from scripts.train import train

MODEL_CLASSES: dict[str, type[nn.Module]] = {
    "BiRNNTagger": BiRNNTagger,
    "BiLSTMTagger": BiLSTMTagger,
    "BiGRUTagger": BiGRUTagger,
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)



def run(
    config: dict,
) -> tuple[nn.Module, list[dict[str, float]], Vocab, DataLoader, torch.device]:
    model_cfg = config["model"]
    train_cfg = config["training"]
    data_cfg = config["data"]

    ds_train = Conll2003Dataset(data_cfg["train_split"])
    ds_val = Conll2003Dataset(data_cfg["val_split"])

    vocab = Vocab(ds_train, tag_key=train_cfg["tag_key"])
    train_dl = get_dataloader(ds_train, batch_size=train_cfg["batch_size"])
    val_dl = get_dataloader(ds_val, batch_size=train_cfg["batch_size"])

    device = torch.device("cpu")
    if torch.cuda.is_available():
        device = torch.device("cuda")
    # elif torch.backends.mps.is_available():
    #     device = torch.device("mps")
    print(f"Using device: {device}")

    model_class = MODEL_CLASSES[model_cfg["type"]]
    model = model_class(
        vocab_size=len(vocab),
        num_classes=vocab.num_tags(),
        embed_dim=model_cfg["embed_dim"],
        hidden_dim=model_cfg["hidden_dim"],
        num_layers=model_cfg["num_layers"],
        dropout=model_cfg["dropout"],
        pad_idx=vocab.token_to_id("<pad>"),
    ).to(device)
    print("Model class is", model_class.__name__)

    optimizer = torch.optim.Adam(model.parameters(), lr=train_cfg["lr"])
    metadata = train(
        model,
        train_dl,
        val_dl,
        vocab,
        optimizer,
        device,
        epochs=train_cfg["epochs"],
        tag_key=train_cfg["tag_key"],
        verbose=train_cfg.get("verbose", True),
    )
    return model, metadata, vocab, val_dl, device


def main(config_path: Path | str = DEFAULT_CONFIG_PATH) -> None:
    config = load_config(config_path)
    model, metadata, vocab, val_dl, device = run(config)

    y_true, y_pred = collect_predictions(
        model, val_dl, vocab, device, tag_key=config["training"]["tag_key"]
    )
    target_names = [vocab.id_to_tag(i) for i in range(vocab.num_tags())]
    print("\nValidation classification report:")
    print(classification_report(y_true, y_pred, target_names=target_names, digits=4))


if __name__ == "__main__":
    main()
