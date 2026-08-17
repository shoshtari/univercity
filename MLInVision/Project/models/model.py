
from dataclasses import dataclass
from typing import Any, Mapping

import torch
from torch import Tensor, nn


class ChannelLayerNorm(nn.Module):

    def __init__(self, channels: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(channels))
        self.bias = nn.Parameter(torch.zeros(channels))
        self.eps = eps

    def forward(self, x: Tensor) -> Tensor:
        mean = x.mean(dim=1, keepdim=True)
        variance = (x - mean).pow(2).mean(dim=1, keepdim=True)
        normalized = (x - mean) * torch.rsqrt(variance + self.eps)
        return normalized * self.weight[:, None, None] + self.bias[:, None, None]


class ConvolutionalModulation(nn.Module):

    def __init__(
        self,
        channels: int,
        kernel_size: int = 11,
        projection_kernel: int = 3,
        use_gating: bool = True,
    ) -> None:
        super().__init__()
        if kernel_size % 2 == 0 or projection_kernel not in (1, 3):
            raise ValueError(
                "Kernel sizes must be odd and projection_kernel must be 1 or 3."
            )
        self.use_gating = use_gating
        if use_gating:
            self.context = nn.Sequential(
                nn.Conv2d(channels, channels, kernel_size=1),
                nn.GELU(),
                nn.Conv2d(
                    channels,
                    channels,
                    kernel_size=kernel_size,
                    padding=kernel_size // 2,
                    groups=channels,
                ),
            )
            self.value = nn.Conv2d(channels, channels, kernel_size=1)
        else:
            self.context = None
            self.value = None
        self.projection = nn.Conv2d(
            channels,
            channels,
            kernel_size=projection_kernel,
            padding=projection_kernel // 2,
        )

    def forward(self, x: Tensor) -> Tensor:
        if self.use_gating:
            x = self.context(x) * self.value(x)
        return self.projection(x)


class DepthwiseMLP(nn.Module):

    def __init__(self, channels: int, expansion_ratio: int = 2) -> None:
        super().__init__()
        hidden_channels = channels * expansion_ratio
        self.expand = nn.Conv2d(channels, hidden_channels, kernel_size=1)
        self.spatial = nn.Conv2d(
            hidden_channels,
            hidden_channels,
            kernel_size=3,
            padding=1,
            groups=hidden_channels,
        )
        self.reduce = nn.Conv2d(hidden_channels, channels, kernel_size=1)
        self.activation = nn.GELU()

    def forward(self, x: Tensor) -> Tensor:
        x = self.activation(self.expand(x))
        x = x + self.activation(self.spatial(x))
        return self.reduce(x)


class Conv2FormerBlock(nn.Module):
    def __init__(
        self,
        channels: int,
        modulation_kernel: int = 11,
        projection_kernel: int = 3,
        mlp_ratio: int = 2,
        use_modulation: bool = True,
        use_gating: bool = True,
        use_mlp: bool = True,
        layer_scale_init: float = 1e-6,
    ) -> None:
        super().__init__()
        self.use_modulation = use_modulation
        self.use_mlp = use_mlp

        if use_modulation:
            self.norm1 = ChannelLayerNorm(channels)
            self.modulation = ConvolutionalModulation(
                channels,
                kernel_size=modulation_kernel,
                projection_kernel=projection_kernel,
                use_gating=use_gating,
            )
            self.layer_scale1 = nn.Parameter(layer_scale_init * torch.ones(channels))
        else:
            self.norm1 = None
            self.modulation = None
            self.register_parameter("layer_scale1", None)

        if use_mlp:
            self.norm2 = ChannelLayerNorm(channels)
            self.mlp = DepthwiseMLP(channels, expansion_ratio=mlp_ratio)
            self.layer_scale2 = nn.Parameter(layer_scale_init * torch.ones(channels))
        else:
            self.norm2 = None
            self.mlp = None
            self.register_parameter("layer_scale2", None)

    def forward(self, x: Tensor) -> Tensor:
        if self.use_modulation:
            update = self.modulation(self.norm1(x))
            x = x + self.layer_scale1[:, None, None] * update
        if self.use_mlp:
            update = self.mlp(self.norm2(x))
            x = x + self.layer_scale2[:, None, None] * update
        return x


class EnhancedSpatialAttention(nn.Module):

    def __init__(self, channels: int, attention_channels: int | None = None) -> None:
        super().__init__()
        hidden = attention_channels or max(1, channels // 4)
        self.reduce = nn.Conv2d(channels, hidden, kernel_size=1)
        self.skip = nn.Conv2d(hidden, hidden, kernel_size=1)
        self.down = nn.Conv2d(hidden, hidden, kernel_size=3, stride=2)
        self.max_conv = nn.Conv2d(hidden, hidden, kernel_size=3, padding=1)
        self.refine1 = nn.Conv2d(hidden, hidden, kernel_size=3, padding=1)
        self.refine2 = nn.Conv2d(hidden, hidden, kernel_size=3, padding=1)
        self.expand = nn.Conv2d(hidden, channels, kernel_size=1)
        self.activation = nn.ReLU(inplace=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: Tensor) -> Tensor:
        reduced = self.reduce(x)
        shortcut = self.skip(reduced)

        low_resolution = self.down(reduced)
        pool_size = min(7, low_resolution.shape[-2], low_resolution.shape[-1])
        if pool_size > 1:
            stride = min(3, pool_size)
            low_resolution = nn.functional.max_pool2d(
                low_resolution, kernel_size=pool_size, stride=stride
            )
        low_resolution = self.activation(self.max_conv(low_resolution))
        low_resolution = self.activation(self.refine1(low_resolution))
        low_resolution = self.refine2(low_resolution)
        low_resolution = nn.functional.interpolate(
            low_resolution,
            size=reduced.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )
        mask = self.sigmoid(self.expand(low_resolution + shortcut))
        return x * mask


class Conv2FormerGroup(nn.Module):

    def __init__(
        self,
        channels: int,
        num_blocks: int,
        modulation_kernel: int = 11,
        projection_kernel: int = 3,
        mlp_ratio: int = 2,
        use_modulation: bool = True,
        use_gating: bool = True,
        use_mlp: bool = True,
        use_group_conv: bool = True,
        use_esa: bool = True,
        layer_scale_init: float = 1e-6,
    ) -> None:
        super().__init__()
        self.blocks = nn.Sequential(
            *[
                Conv2FormerBlock(
                    channels,
                    modulation_kernel=modulation_kernel,
                    projection_kernel=projection_kernel,
                    mlp_ratio=mlp_ratio,
                    use_modulation=use_modulation,
                    use_gating=use_gating,
                    use_mlp=use_mlp,
                    layer_scale_init=layer_scale_init,
                )
                for _ in range(num_blocks)
            ]
        )
        self.local_conv = (
            nn.Conv2d(channels, channels, kernel_size=3, padding=1)
            if use_group_conv
            else nn.Identity()
        )
        self.esa = EnhancedSpatialAttention(channels) if use_esa else nn.Identity()

    def forward(self, x: Tensor) -> Tensor:
        return self.esa(self.local_conv(self.blocks(x)))


@dataclass(frozen=True)
class STSNOptions:

    scale: int = 2
    channels: int = 50
    num_groups: int = 4
    blocks_per_group: int = 4
    modulation_kernel: int = 11
    projection_kernel: int = 3
    mlp_ratio: int = 2
    use_modulation: bool = True
    use_gating: bool = True
    use_mlp: bool = True
    use_group_conv: bool = True
    use_esa: bool = True
    layer_scale_init: float = 1e-6


class STSN(nn.Module):

    def __init__(self, options: STSNOptions | None = None, **kwargs: Any) -> None:
        super().__init__()
        if options is not None and kwargs:
            raise ValueError("Pass either STSNOptions or keyword options, not both.")
        self.options = options or STSNOptions(**kwargs)
        opt = self.options
        if opt.scale not in (2, 3, 4):
            raise ValueError("STSN supports scale factors 2, 3 and 4.")

        self.shallow = nn.Conv2d(3, opt.channels, kernel_size=3, padding=1)
        self.groups = nn.ModuleList(
            [
                Conv2FormerGroup(
                    opt.channels,
                    opt.blocks_per_group,
                    modulation_kernel=opt.modulation_kernel,
                    projection_kernel=opt.projection_kernel,
                    mlp_ratio=opt.mlp_ratio,
                    use_modulation=opt.use_modulation,
                    use_gating=opt.use_gating,
                    use_mlp=opt.use_mlp,
                    use_group_conv=opt.use_group_conv,
                    use_esa=opt.use_esa,
                    layer_scale_init=opt.layer_scale_init,
                )
                for _ in range(opt.num_groups)
            ]
        )
        fused_channels = opt.channels * (opt.num_groups + 1)
        self.fusion = nn.Sequential(
            nn.Conv2d(fused_channels, opt.channels, kernel_size=1),
            nn.Conv2d(opt.channels, opt.channels, kernel_size=3, padding=1),
        )
        self.reconstruction = nn.Sequential(
            nn.Conv2d(
                opt.channels,
                3 * opt.scale * opt.scale,
                kernel_size=3,
                padding=1,
            ),
            nn.PixelShuffle(opt.scale),
        )
        self.apply(self._initialize_weights)

    @staticmethod
    def _initialize_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Conv2d):
            nn.init.kaiming_normal_(module.weight, mode="fan_in", nonlinearity="linear")
            if module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward_features(self, x: Tensor) -> Tensor:
        shallow = self.shallow(x)
        group_outputs = []
        features = shallow
        for group in self.groups:
            features = group(features)
            group_outputs.append(features)
        combined = self.fusion(torch.cat([shallow, *group_outputs], dim=1))
        return combined + shallow

    def forward(self, x: Tensor) -> Tensor:
        return self.reconstruction(self.forward_features(x))


def build_model(config: Mapping[str, Any]) -> STSN:
    model_config = dict(config.get("model", config))
    allowed = set(STSNOptions.__dataclass_fields__)
    options = {key: value for key, value in model_config.items() if key in allowed}
    return STSN(STSNOptions(**options))


def count_parameters(model: nn.Module, trainable_only: bool = True) -> int:
    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad or not trainable_only
    )
