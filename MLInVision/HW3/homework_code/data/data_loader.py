import csv
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import cv2 as cv
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

RGBColor = tuple[int, int, int]


@dataclass(frozen=True)
class SegmentationSample:
    image_path: Path
    mask_ref: Path

def _sorted_image_files(images_dir: Path) -> list[Path]:
    image_files = sorted(
        images_dir.glob("*.*"),
        key=lambda path: path.name,
    )
    return image_files



class SegmentationDatasetBase(ABC):
    def __init__(
        self,
        samples: list[SegmentationSample],
    ) -> None:
        self.samples = samples
        self._color_keys_cache: np.ndarray | None = None
        self._color_indices_cache: np.ndarray | None = None

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        sample = self.samples[index]
        image = self._load_image(sample.image_path)
        mask = self._load_mask(sample.mask_ref)

        image_tensor = torch.from_numpy(image).float() / 255.0
        mask_tensor = torch.from_numpy(mask).long()
        mask_tensor = self._encode_mask(mask_tensor)

        return image_tensor, mask_tensor

    def _encode_mask(self, mask: torch.Tensor) -> torch.Tensor:
        color_keys, color_indices = self._get_color_encoding()
        mask_array = mask.detach().cpu().numpy().astype(np.uint32, copy=False)
        packed_mask = (
            (mask_array[..., 0] << 16)
            | (mask_array[..., 1] << 8)
            | mask_array[..., 2]
        )

        lookup_positions = np.searchsorted(color_keys, packed_mask)
        valid_positions = lookup_positions < color_keys.size
        matches = np.zeros_like(lookup_positions, dtype=bool)
        matches[valid_positions] = (
            color_keys[lookup_positions[valid_positions]] == packed_mask[valid_positions]
        )

        if not np.all(matches):
            unknown_keys = np.unique(packed_mask[~matches])
            unknown_colors = [self._unpack_color_key(color_key) for color_key in unknown_keys]
            raise ValueError(f"Unknown mask color(s): {unknown_colors}")

        mask_indices = color_indices[lookup_positions]
        return torch.from_numpy(mask_indices.astype(np.int64, copy=False))

    def _get_color_encoding(self) -> tuple[np.ndarray, np.ndarray]:
        if self._color_keys_cache is None or self._color_indices_cache is None:
            colors = self._get_colors()
            color_keys = np.array([self._pack_color(color) for color in colors], dtype=np.uint32)
            sorted_order = np.argsort(color_keys)
            self._color_keys_cache = color_keys[sorted_order]
            self._color_indices_cache = np.asarray(sorted_order, dtype=np.int64)
        return self._color_keys_cache, self._color_indices_cache

    @staticmethod
    def _pack_color(color: RGBColor) -> int:
        red, green, blue = color
        return (red << 16) | (green << 8) | blue

    @staticmethod
    def _unpack_color_key(color_key: np.uint32 | int) -> RGBColor:
        packed = int(color_key)
        return ((packed >> 16) & 255, (packed >> 8) & 255, packed & 255)


    @abstractmethod
    def _load_image(self, path: Path) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def _load_mask(self, mask_ref: Path | int) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def _get_colors(self) -> list[RGBColor]:
        raise NotImplementedError



class Dataset1SegmentationDataset(SegmentationDatasetBase):
    def __init__(
        self,
        root_dir: str | Path,
    ) -> None:
        self.root_dir = Path(root_dir)
        self.images_dir = self.root_dir / "images"
        self.masks_dir = self.root_dir / "masks"
        self.labels_csv = self.root_dir / "Labels and Colors.csv"

        image_files = _sorted_image_files(self.images_dir)
        samples = [
            SegmentationSample(
                image_path=image_path,
                mask_ref=self.masks_dir / image_path.name,
            )
            for image_path in image_files
        ]

        super().__init__(samples=samples)

    def _load_image(self, path: Path) -> np.ndarray:
        image = cv.imread(str(path), cv.IMREAD_COLOR)
        assert image is not None
        return cv.cvtColor(image, cv.COLOR_BGR2RGB)

    def _load_mask(self, path: Path) -> np.ndarray:
        mask = cv.imread(str(path), cv.IMREAD_COLOR)
        assert mask is not None
        return cv.cvtColor(mask, cv.COLOR_BGR2RGB)

    def _get_colors(self) -> Sequence[RGBColor]:
        colors = ((237,34,236),  (201,158,74),  (96,32,192),  (89,134,179),  (153,223,219),  (255,106,77), 
(22,100,252), (143,182,45), (38,198,129), (27,154,218), (0,0,0))
        return colors

def _read_coco_annotations(json_path: Path):
    with json_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    images_by_id = {image["id"]: image for image in data["images"]}
    annotations_by_image_id: dict[int, list[dict]] = {}
    for annotation in data["annotations"]:
        annotations_by_image_id.setdefault(annotation["image_id"], []).append(
            annotation
        )

    categories = sorted(data["categories"], key=lambda item: item["id"])
    category_id_to_index = {
        category["id"]: index + 1 for index, category in enumerate(categories)
    }
    category_names = [category["name"] for category in categories]

    return images_by_id, annotations_by_image_id, category_id_to_index, category_names


class Dataset2SegmentationDataset(SegmentationDatasetBase):

    def __init__(
        self,
        root_dir: str | Path,
    ) -> None:
        self.root_dir = Path(root_dir)
        self.images_dir = self.root_dir / "images"
        self.annotation_file = self.root_dir / "COCO_Football Pixel.json"

        (
            self.images_by_id,
            self.annotations_by_image_id,
            self.category_id_to_index,
            self.class_names,
        ) = _read_coco_annotations(self.annotation_file)

        image_records = sorted(
            self.images_by_id.values(), key=lambda item: item["file_name"]
        )
        if not image_records:
            raise FileNotFoundError(f"No image records found in {self.annotation_file}")

        samples = [
            SegmentationSample(
                image_path=self.images_dir / record["file_name"],
                mask_ref=record["id"],
            )
            for record in image_records
        ]

        super().__init__(samples=samples)

    def _load_image(self, path: Path) -> np.ndarray:
        image = cv.imread(str(path), cv.IMREAD_COLOR)
        assert image is not None
        return cv.cvtColor(image, cv.COLOR_BGR2RGB)

    def _load_mask(self, image_id: int) -> np.ndarray:
        mask = cv.imread(str(self.images_dir / self.images_by_id[image_id]["file_name"]), cv.IMREAD_COLOR)
        assert mask is not None
        return cv.cvtColor(mask, cv.COLOR_BGR2RGB)
    
    def _get_colors(self) -> Sequence[RGBColor]:
        colors = ((0, 0, 0), (27, 71, 151), (111, 48, 253), (137, 126, 126), (201, 19, 223), (238, 171, 171), 
(254, 233, 3), (255, 0, 29), (255, 159, 0), (255, 160, 1), (255, 235, 0))
        return colors


def get_dataloader(
    ds: Dataset,
    batch_size: int = 4,
    shuffle: bool = True,
    num_workers: int = 0,
) -> DataLoader:
    return DataLoader(
        ds, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers
    )
