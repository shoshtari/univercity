
import copy
import sys
import tempfile
import unittest
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.data_loader import SuperResolutionDataset, generate_demo_dataset
from models.model import build_model, count_parameters
from scripts.ablation import EXPECTED_X2, variant_config
from utils.config import load_config


class ModelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(PROJECT_ROOT / "config" / "config.yaml")

    def test_published_parameter_counts(self) -> None:
        for variant, expected in EXPECTED_X2.items():
            with self.subTest(variant=variant):
                model = build_model(variant_config(self.config, variant))
                self.assertEqual(count_parameters(model), expected)

    def test_output_shape_for_all_scales(self) -> None:
        for scale in (2, 3, 4):
            config = copy.deepcopy(self.config)
            config["model"]["scale"] = scale
            model = build_model(config).eval()
            with torch.inference_mode():
                output = model(torch.rand(1, 3, 12, 10))
            self.assertEqual(tuple(output.shape), (1, 3, 12 * scale, 10 * scale))


class DataTests(unittest.TestCase):

    def test_generated_pair_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            train_dir, _ = generate_demo_dataset(
                Path(temporary), train_count=2, val_count=1, image_size=64
            )
            dataset = SuperResolutionDataset(
                train_dir, 2, training=True, hr_patch_size=48, augment=True
            )
            sample = dataset[0]
            self.assertEqual(tuple(sample["lr"].shape), (3, 24, 24))
            self.assertEqual(tuple(sample["hr"].shape), (3, 48, 48))


if __name__ == "__main__":
    unittest.main()
