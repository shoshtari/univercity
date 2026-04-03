from models.model import MLP
from config import Config
import yaml
from data.data_loader import load_data
from models.loss import CrossEntropyLoss
import numpy as np


def create_and_train_model_from_config(cfg: Config, return_logs: bool = False):
    np.random.seed(42)
    data = load_data()
    model = MLP(
        layers=cfg.layers,
        loss="cross_entropy",
        normalize_input=cfg.normalize,
        early_stopping_threshold=cfg.early_stopping_threshold,
    )
    logs = model.fit(
        X_train=data.X_train,
        y_train=data.y_train,
        X_val=data.X_val,
        y_val=data.y_val,
        epochs=cfg.epochs,
        batch_size=cfg.batch_size,
        logging_step=cfg.logging_step,
        logging_enable_print=cfg.logging_enable_print,
    )
    if return_logs:
        return model, logs
    return model


if __name__ == "__main__":
    cfg = Config.read_yaml()
    print(cfg)
    create_and_train_model_from_config(cfg)
