from dataclasses import dataclass
from typing import Iterable
from models.layer import Layer
import yaml

DEFAULT_PATHS = (
    "./config/config.yaml",
    "../config/config.yaml",
)


@dataclass
class Config:
    epochs: int
    layers: list[Layer]
    normalize: bool
    batch_size: int
    logging_step: int
    logging_enable_print: bool
    early_stopping_threshold: int

    @classmethod
    def read_yaml(cls, paths: Iterable[str] = DEFAULT_PATHS) -> "Config":
        for path in paths:
            try:
                with open(path, "rt") as f:
                    data = yaml.safe_load(f)
                f.close()
                break
            except FileNotFoundError:
                pass
        else:
            raise ValueError("couldn't find config file")

        return cls(
            epochs=data["epochs"],
            normalize=data["normalize"],
            batch_size=data["batch_size"],
            logging_step=data.get("logging_step", 10),
            logging_enable_print=data["logging_enable_print"],
            early_stopping_threshold=data["early_stopping_threshold"],
            layers=Layer.get_layers(
                hidden_layer_sizes=data["layers_sizes"],
                momentum=data["momentum"],
                learning_rate=float(data["learning_rate"]),
                regularization_factor=data["regularization_factor"],
            ),
        )
