from __future__ import annotations

import torch
import torchaudio
import torchaudio.functional as F
from transformers import HubertModel, Wav2Vec2FeatureExtractor

from config import AppConfig
from utils.torch_device import get_device

MEL_EXTRACTOR = "mel_spectrogram"
HUBERT_EXTRACTOR = "hubert"


class MelSpectrogramExtractor:
    def __init__(self, cfg: AppConfig) -> None:
        feat = cfg.feature
        ds = cfg.dataset
        self.sample_rate = ds.sample_rate
        self.mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.sample_rate,
            n_fft=512,
            hop_length=128,
            n_mels=feat.n_mels,
            power=2.0,
        )
        self.db = torchaudio.transforms.AmplitudeToDB()

    def __call__(self, waveform: torch.Tensor) -> torch.Tensor:
        mel = self.mel(waveform)
        mel = self.db(mel)
        return mel


class HubertExtractor:
    def __init__(self, cfg: AppConfig) -> None:
        ds = cfg.dataset
        self.model_name = "facebook/hubert-base-ls960"
        self.layer = -1
        self.sample_rate = ds.sample_rate
        self.device = get_device()
        self.model = HubertModel.from_pretrained(self.model_name)
        self.model = self.model.to(self.device).eval()
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
            self.model_name
        )

    @torch.no_grad()
    def __call__(self, waveform: torch.Tensor) -> torch.Tensor:
        inputs = self.feature_extractor(
            waveform.cpu().numpy(),
            sampling_rate=self.sample_rate,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        outputs = self.model(**inputs, output_hidden_states=True)
        hidden = outputs.hidden_states[self.layer]
        return hidden.squeeze(0).cpu()


def build_extractor(name: str, cfg: AppConfig):
    if name == MEL_EXTRACTOR:
        return MelSpectrogramExtractor(cfg)
    if name == HUBERT_EXTRACTOR:
        return HubertExtractor(cfg)
    raise ValueError(f"Unknown feature extractor: {name!r}")
