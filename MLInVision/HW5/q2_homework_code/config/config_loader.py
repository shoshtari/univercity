import yaml
from pathlib import Path


def load_config(path="config.yaml"):
    with open(Path(__file__).resolve().parent / path, "r") as f:
        return yaml.safe_load(f)
