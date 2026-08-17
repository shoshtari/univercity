
import math
from dataclasses import dataclass

import numpy as np
import torch
from skimage.metrics import structural_similarity
from torch import Tensor


def rgb_to_y(image: Tensor) -> Tensor:
    if image.ndim == 3:
        image = image.unsqueeze(0)
    if image.ndim != 4 or image.shape[1] != 3:
        raise ValueError("Expected an RGB tensor with shape CHW or BCHW.")
    weights = image.new_tensor([65.481, 128.553, 24.966]).view(1, 3, 1, 1)
    return (image * weights).sum(dim=1, keepdim=True) / 255.0 + 16.0 / 255.0


def shave_border(image: Tensor, border: int) -> Tensor:
    if border <= 0:
        return image
    if image.shape[-2] <= 2 * border or image.shape[-1] <= 2 * border:
        raise ValueError("Image is too small for the requested border shave.")
    return image[..., border:-border, border:-border]


def psnr(prediction: Tensor, target: Tensor, data_range: float = 1.0) -> float:
    error = torch.mean((prediction.double() - target.double()).pow(2)).item()
    if error == 0:
        return float("inf")
    return 10.0 * math.log10((data_range * data_range) / error)


def ssim(prediction: Tensor, target: Tensor, data_range: float = 1.0) -> float:
    prediction_array = prediction.detach().cpu().squeeze().double().numpy()
    target_array = target.detach().cpu().squeeze().double().numpy()
    smallest_side = min(prediction_array.shape[-2:])
    win_size = min(11, smallest_side if smallest_side % 2 else smallest_side - 1)
    if win_size < 3:
        raise ValueError("Image is too small for SSIM.")
    return float(
        structural_similarity(
            target_array,
            prediction_array,
            data_range=data_range,
            gaussian_weights=True,
            sigma=1.5,
            use_sample_covariance=False,
            win_size=win_size,
        )
    )


@dataclass
class MetricAccumulator:

    psnr_sum: float = 0.0
    ssim_sum: float = 0.0
    time_sum_ms: float = 0.0
    count: int = 0

    def update(
        self, psnr_value: float, ssim_value: float, time_ms: float = 0.0
    ) -> None:
        self.psnr_sum += psnr_value
        self.ssim_sum += ssim_value
        self.time_sum_ms += time_ms
        self.count += 1

    def averages(self) -> dict[str, float | int]:
        if self.count == 0:
            return {
                "psnr": float("nan"),
                "ssim": float("nan"),
                "time_ms": float("nan"),
                "count": 0,
            }
        return {
            "psnr": self.psnr_sum / self.count,
            "ssim": self.ssim_sum / self.count,
            "time_ms": self.time_sum_ms / self.count,
            "count": self.count,
        }


def evaluate_pair(
    prediction: Tensor, target: Tensor, scale: int
) -> tuple[float, float]:
    prediction_y = shave_border(rgb_to_y(prediction.clamp(0, 1)), scale)
    target_y = shave_border(rgb_to_y(target.clamp(0, 1)), scale)
    return psnr(prediction_y, target_y), ssim(prediction_y, target_y)
