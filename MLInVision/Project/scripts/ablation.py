
import copy
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.model import build_model, count_parameters
from utils.config import load_config

EXPECTED_X2 = {
    "full": 881_912,
    "projection_1x1": 561_912,
    "without_attention_gating": 702_712,
    "without_modulation": 339_512,
    "without_mlp": 701_112,
    "without_esa": 855_312,
    "without_group_conv": 791_712,
}


def variant_config(base: dict, variant: str) -> dict:
    config = copy.deepcopy(base)
    changes = {
        "full": {},
        "projection_1x1": {"projection_kernel": 1},
        "without_attention_gating": {"use_gating": False},
        "without_modulation": {"use_modulation": False},
        "without_mlp": {"use_mlp": False},
        "without_esa": {"use_esa": False},
        "without_group_conv": {"use_group_conv": False},
    }
    config["model"].update(changes[variant])
    return config


def main() -> None:
    config = load_config(PROJECT_ROOT / "config" / "config.yaml")
    if int(config["model"]["scale"]) != 2:
        raise ValueError("The published ablation parameter table is for scale x2.")
    results = {}
    for name, expected in EXPECTED_X2.items():
        actual = count_parameters(build_model(variant_config(config, name)))
        results[name] = {
            "actual": actual,
            "expected": expected,
            "matches": actual == expected,
        }
    print(json.dumps(results, indent=2))
    if not all(item["matches"] for item in results.values()):
        raise SystemExit(
            "At least one parameter count does not match the paper-derived value."
        )


if __name__ == "__main__":
    main()
