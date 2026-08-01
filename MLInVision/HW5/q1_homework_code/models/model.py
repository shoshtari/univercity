import torch
import torch.nn as nn

from config import AppConfig


class CNNModel(nn.Module):
    def __init__(self, cfg: AppConfig):
        super().__init__()
        n_classes = len(cfg.dataset.emotions)
        n_layers = cfg.training.cnn_layers

        channels = [1, 32, 64, 128]
        self.layers = nn.ModuleList()
        for i in range(n_layers):
            in_ch = channels[i]
            out_ch = channels[i + 1]
            self.layers.append(nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1))
            self.layers.append(nn.BatchNorm2d(out_ch))
            self.layers.append(nn.ReLU())
            self.layers.append(nn.MaxPool2d(kernel_size=2))

        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        flat_dim = channels[n_layers]
        self.fc = nn.Linear(flat_dim, n_classes)

    def forward(self, x):
        x = x.unsqueeze(1)
        for layer in self.layers:
            x = layer(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        return self.fc(x)


class MLPModel(nn.Module):
    def __init__(self, cfg: AppConfig) -> None:
        super().__init__()
        n_classes = len(cfg.dataset.emotions)
        n_layers = cfg.training.mlp_layers
        hidden_dim = 256
        input_dim = 768
        dropout = cfg.training.dropout

        layers = []
        dims = [input_dim] + [hidden_dim] * n_layers
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
        layers.append(nn.Linear(dims[-1], n_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        if x.dim() == 2:
            x = x.mean(dim=0, keepdim=True)
        elif x.dim() == 3:
            x = x.mean(dim=1)
        else:
            raise ValueError(f"MLPModel expects 2D or 3D input, got {x.dim()}D")
        return self.net(x)


def build_model(cfg: AppConfig, override_extractor: str | None = None) -> nn.Module:
    extractor = override_extractor
    if extractor is None:
        extractor = cfg.feature.extractor

    if extractor == "mel_spectrogram":
        return CNNModel(cfg)
    if extractor == "hubert":
        return MLPModel(cfg)
    raise ValueError(f"No model defined for extractor: {extractor}")
