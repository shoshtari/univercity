import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import torch
from PIL import Image, ImageDraw
from torch import Tensor
from torch.utils.data import DataLoader, Dataset

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def resolve_project_path(project_root: Path, value: str | Path | None) -> Path | None:
    if value in (None, ""):
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def find_images(directory: Path, max_images: int | None = None) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(
            f"Image directory does not exist: {directory}. "
            "Download the data or run scripts/main.py --quick."
        )
    images = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        images = sorted(
            path
            for path in directory.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )
    if max_images is not None:
        images = images[:max_images]
    if not images:
        raise RuntimeError(f"No supported images were found in {directory}.")
    return images


def mod_crop(image: Image.Image, scale: int) -> Image.Image:
    width = image.width - image.width % scale
    height = image.height - image.height % scale
    return image.crop((0, 0, width, height))


def bicubic_downsample(image: Image.Image, scale: int) -> Image.Image:
    return image.resize(
        (image.width // scale, image.height // scale),
        resample=Image.Resampling.BICUBIC,
    )


def image_to_tensor(image: Image.Image) -> Tensor:
    array = np.asarray(image, dtype=np.float32) / 255.0
    return torch.from_numpy(np.ascontiguousarray(array.transpose(2, 0, 1)))


def tensor_to_image(tensor: Tensor) -> Image.Image:
    array = tensor.detach().cpu().clamp(0.0, 1.0).permute(1, 2, 0).numpy()
    return Image.fromarray(np.rint(array * 255.0).astype(np.uint8), mode="RGB")


def _normalized_stem(path: Path, scale: int) -> str:
    stem = path.stem.lower()
    for suffix in (f"x{scale}", f"_x{scale}", f"-x{scale}", "_lr", "_hr"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem


class SuperResolutionDataset(Dataset[dict[str, Tensor | str]]):

    def __init__(
        self,
        hr_dir: Path,
        scale: int,
        *,
        lr_dir: Path | None = None,
        training: bool = False,
        hr_patch_size: int | None = None,
        augment: bool = True,
        repeat: int = 1,
        max_images: int | None = None,
    ) -> None:
        super().__init__()
        if scale not in (2, 3, 4):
            raise ValueError("Scale must be 2, 3 or 4.")
        if hr_patch_size is not None and hr_patch_size % scale:
            raise ValueError("hr_patch_size must be divisible by scale.")
        self.hr_paths = find_images(hr_dir, max_images=max_images)
        self.scale = scale
        self.training = training
        self.hr_patch_size = hr_patch_size
        self.augment = augment and training
        self.repeat = max(1, int(repeat))
        self.lr_by_stem: dict[str, Path] = {}
        if lr_dir is not None and lr_dir.exists():
            self.lr_by_stem = {
                _normalized_stem(path, scale): path for path in find_images(lr_dir)
            }

    def __len__(self) -> int:
        return len(self.hr_paths) * self.repeat

    def _load_pair(self, hr_path: Path) -> tuple[Image.Image, Image.Image]:
        with Image.open(hr_path) as image:
            hr = mod_crop(image.convert("RGB"), self.scale)
        lr_path = self.lr_by_stem.get(_normalized_stem(hr_path, self.scale))
        if lr_path is None:
            lr = bicubic_downsample(hr, self.scale)
        else:
            with Image.open(lr_path) as image:
                lr = image.convert("RGB")
            aligned_width = min(hr.width, lr.width * self.scale)
            aligned_height = min(hr.height, lr.height * self.scale)
            aligned_width -= aligned_width % self.scale
            aligned_height -= aligned_height % self.scale
            hr = hr.crop((0, 0, aligned_width, aligned_height))
            lr = lr.crop(
                (0, 0, aligned_width // self.scale, aligned_height // self.scale)
            )
        return lr, hr

    def _random_crop(
        self, lr: Image.Image, hr: Image.Image
    ) -> tuple[Image.Image, Image.Image]:
        if self.hr_patch_size is None:
            return lr, hr
        patch_hr = min(self.hr_patch_size, hr.width, hr.height)
        patch_hr -= patch_hr % self.scale
        patch_lr = patch_hr // self.scale
        if patch_lr < 1:
            raise ValueError("Images are smaller than one low-resolution pixel.")
        max_left = lr.width - patch_lr
        max_top = lr.height - patch_lr
        left_lr = random.randint(0, max_left) if max_left > 0 else 0
        top_lr = random.randint(0, max_top) if max_top > 0 else 0
        lr = lr.crop((left_lr, top_lr, left_lr + patch_lr, top_lr + patch_lr))
        left_hr, top_hr = left_lr * self.scale, top_lr * self.scale
        hr = hr.crop((left_hr, top_hr, left_hr + patch_hr, top_hr + patch_hr))
        return lr, hr

    def _augment_pair(
        self, lr: Image.Image, hr: Image.Image
    ) -> tuple[Image.Image, Image.Image]:
        if random.random() < 0.5:
            lr = lr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            hr = hr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        rotation = random.randrange(4)
        if rotation:
            methods = {
                1: Image.Transpose.ROTATE_90,
                2: Image.Transpose.ROTATE_180,
                3: Image.Transpose.ROTATE_270,
            }
            lr = lr.transpose(methods[rotation])
            hr = hr.transpose(methods[rotation])
        return lr, hr

    def __getitem__(self, index: int) -> dict[str, Tensor | str]:
        hr_path = self.hr_paths[index % len(self.hr_paths)]
        lr, hr = self._load_pair(hr_path)
        if self.training:
            lr, hr = self._random_crop(lr, hr)
        if self.augment:
            lr, hr = self._augment_pair(lr, hr)
        return {
            "lr": image_to_tensor(lr),
            "hr": image_to_tensor(hr),
            "name": hr_path.stem,
        }


def _data_value(config: Mapping[str, Any], key: str, default: Any = None) -> Any:
    return config.get("data", {}).get(key, default)


def build_dataloaders(
    config: Mapping[str, Any], project_root: Path, *, quick: bool = False
) -> tuple[DataLoader[Any], DataLoader[Any]]:
    scale = int(config["model"]["scale"])
    quick_cfg = config.get("quick", {}) if quick else {}
    train_hr = resolve_project_path(
        project_root, quick_cfg.get("train_hr_dir", _data_value(config, "train_hr_dir"))
    )
    train_lr = resolve_project_path(
        project_root, quick_cfg.get("train_lr_dir", _data_value(config, "train_lr_dir"))
    )
    if train_hr is None:
        raise ValueError("train_hr_dir must be configured.")

    training_cfg = config.get("training", {})
    train_dataset = SuperResolutionDataset(
        train_hr,
        scale,
        lr_dir=train_lr,
        training=True,
        hr_patch_size=int(
            quick_cfg.get("hr_patch_size", _data_value(config, "hr_patch_size"))
        ),
        augment=bool(_data_value(config, "augment", True)),
        repeat=int(quick_cfg.get("repeat", _data_value(config, "repeat", 1))),
        max_images=quick_cfg.get("max_train_images"),
    )
    batch_size = int(quick_cfg.get("batch_size", training_cfg.get("batch_size", 32)))
    workers = int(quick_cfg.get("num_workers", _data_value(config, "num_workers", 0)))
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=len(train_dataset) >= batch_size,
        persistent_workers=workers > 0,
    )
    val_loader = build_validation_dataloader(config, project_root, quick=quick)
    return train_loader, val_loader


def build_validation_dataloader(
    config: Mapping[str, Any], project_root: Path, *, quick: bool = False
) -> DataLoader[Any]:
    scale = int(config["model"]["scale"])
    quick_cfg = config.get("quick", {}) if quick else {}
    val_hr = resolve_project_path(
        project_root, quick_cfg.get("val_hr_dir", _data_value(config, "val_hr_dir"))
    )
    val_lr = resolve_project_path(
        project_root, quick_cfg.get("val_lr_dir", _data_value(config, "val_lr_dir"))
    )
    if val_hr is None:
        raise ValueError("val_hr_dir must be configured.")
    val_dataset = SuperResolutionDataset(
        val_hr,
        scale,
        lr_dir=val_lr,
        training=False,
        max_images=quick_cfg.get("max_val_images"),
    )
    workers = int(quick_cfg.get("num_workers", _data_value(config, "num_workers", 0)))
    return DataLoader(
        val_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=workers,
        persistent_workers=workers > 0,
    )


def _procedural_image(size: int, index: int, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed + index)
    yy, xx = np.mgrid[0:size, 0:size]
    phase = rng.uniform(0, math.tau)
    red = 127.5 + 60 * np.sin(xx / (4.0 + index % 5) + phase) + 35 * yy / size
    green = 110 + 70 * np.cos((xx + yy) / (7.0 + index % 3)) + 40 * xx / size
    blue = 100 + 60 * np.sin(np.hypot(xx - size / 2, yy - size / 2) / 3.5)
    array = np.stack([red, green, blue], axis=-1).clip(0, 255).astype(np.uint8)
    image = Image.fromarray(array, mode="RGB")
    draw = ImageDraw.Draw(image)
    for shape_index in range(7):
        x0 = int(rng.integers(0, max(1, size - 24)))
        y0 = int(rng.integers(0, max(1, size - 24)))
        width = int(rng.integers(10, max(11, size // 3)))
        color = tuple(int(value) for value in rng.integers(20, 236, size=3))
        if shape_index % 2:
            draw.rectangle(
                (x0, y0, min(size - 1, x0 + width), min(size - 1, y0 + width)),
                outline=color,
                width=2,
            )
        else:
            draw.ellipse(
                (x0, y0, min(size - 1, x0 + width), min(size - 1, y0 + width)),
                outline=color,
                width=2,
            )
    return image


def generate_demo_dataset(
    dataset_root: Path,
    *,
    train_count: int = 8,
    val_count: int = 4,
    image_size: int = 128,
    seed: int = 810104039,
) -> tuple[Path, Path]:
    train_dir = dataset_root / "demo" / "train_hr"
    val_dir = dataset_root / "demo" / "val_hr"
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    for index in range(train_count):
        path = train_dir / f"train_{index + 1:02d}.png"
        if not path.exists():
            _procedural_image(image_size, index, seed).save(path)
    for index in range(val_count):
        path = val_dir / f"val_{index + 1:02d}.png"
        if not path.exists():
            _procedural_image(image_size, index + train_count, seed).save(path)
    return train_dir, val_dir
