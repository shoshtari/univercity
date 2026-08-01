from __future__ import annotations

import os
from dataclasses import dataclass

import yaml

_CONFIG_PATHS = (
    "./config/config.yaml",
    "../config/config.yaml",
)


@dataclass(frozen=True)
class DatasetConfig:
    sample_rate: int
    voice_length_seconds: int
    emotions: list[str]
    seed: int
    split_ratios: dict[str, float]
    speakers: dict[str, int]


@dataclass(frozen=True)
class FeatureConfig:
    extractor: str
    n_mels: int


@dataclass(frozen=True)
class TrainingConfig:
    batch_size: int
    epochs: int
    learning_rate: float
    optimizer: str
    loss_function: str
    cnn_layers: int
    mlp_layers: int
    dropout: float


@dataclass(frozen=True)
class EnvironmentConfig:
    hf_offline: bool


@dataclass(frozen=True)
class AppConfig:
    dataset: DatasetConfig
    feature: FeatureConfig
    training: TrainingConfig
    environment: EnvironmentConfig


for cfg_path in _CONFIG_PATHS:
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as _f:
            _raw = yaml.safe_load(_f) or {}
        break
else:
    raise ValueError("config not found")

config = AppConfig(
    dataset=DatasetConfig(**_raw["dataset"]),
    feature=FeatureConfig(**_raw["feature"]),
    training=TrainingConfig(**_raw["training"]),
    environment=EnvironmentConfig(**_raw["environment"]),
)

if config.environment.hf_offline:
    os.environ["HF_HUB_OFFLINE"] = "1"
