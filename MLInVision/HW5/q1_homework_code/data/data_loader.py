import os
import random

import torch
import torchaudio
import torch.nn.functional as F
from cachetools import cached
from torch.utils.data import Dataset

from config import config
from utils.features import build_extractor

_EMOTION_LABELS = {"ANG": 0, "DIS": 1, "FEA": 2, "HAP": 3, "NEU": 4, "SAD": 5}


def _build_label_map(emotion_whitelist: set[str]) -> dict[str, int]:
    whitelist = sorted(emotion_whitelist)
    return {emotion: idx for idx, emotion in enumerate(whitelist)}


AUDIO_DIRS = (
    "./data/dataset/AudioWAV",
    "../data/dataset/AudioWAV",
)


def collate_fn(batch):
    features_list = [b["features"] for b in batch]
    labels = torch.stack([b["label"] for b in batch])

    max_len = max(f.shape[0] for f in features_list)
    padded = []
    for feat in features_list:
        if feat.shape[0] < max_len:
            pad_len = max_len - feat.shape[0]
            feat = F.pad(feat, (0, 0, 0, pad_len))
        padded.append(feat)
    features = torch.stack(padded)
    return {"features": features, "label": labels}


def _parse_filename(filename: str) -> tuple[int, str] | None:
    name = filename.rsplit(".", 1)[0]
    parts = name.split("_")
    assert len(parts) == 4
    actor_id = int(parts[0])
    return actor_id, parts[2]


@cached(cache={})
def _get_resampler(src_sr: int, tgt_sr: int) -> torchaudio.transforms.Resample | None:
    return torchaudio.transforms.Resample(src_sr, tgt_sr)


def _unify_length(waveform: torch.Tensor, target_len: int) -> torch.Tensor:
    if waveform.shape[-1] >= target_len:
        return waveform[..., :target_len]
    pad = target_len - waveform.shape[-1]
    return torch.nn.functional.pad(waveform, (0, pad))


def _load_waveform(path: str, target_sr: int) -> torch.Tensor:
    waveform, sr = torchaudio.load(path)
    if sr != target_sr:
        resampler = _get_resampler(sr, target_sr)
        if resampler is not None:
            waveform = resampler(waveform)
    return waveform.squeeze(0)


def _scan_files(
    audio_dir: str,
    emotion_whitelist: set[str],
    max_speakers: int | None,
) -> list[tuple[str, int, str]]:
    files: list[tuple[str, int, str]] = []
    for f in sorted(os.listdir(audio_dir)):
        parsed = _parse_filename(f)
        if parsed is None:
            continue
        actor_id, emotion = parsed
        if emotion not in emotion_whitelist:
            continue
        files.append((os.path.join(audio_dir, f), actor_id, emotion))

    actor_ids = list(set({aid for _, aid, _ in files}))
    actor_ids.sort()
    dset = config.dataset
    rng = random.Random(dset.seed)
    rng.shuffle(actor_ids)

    n = max_speakers if max_speakers is not None else len(actor_ids)
    keep_actors = set(actor_ids[:n])

    return list(filter(lambda x: x[1] in keep_actors, files))


def _compute_split(
    samples: list[tuple[str, int, str]],
    split: str,
    seed: int,
    ratios: dict[str, float],
    label_map: dict[str, int],
) -> list[tuple[str, int]]:
    actor_ids = sorted({aid for _, aid, _ in samples})
    rng = random.Random(seed)
    rng.shuffle(actor_ids)

    n = len(actor_ids)
    n_train = int(n * ratios["train"])
    n_val = int(n * ratios["val"])
    train_set = set(actor_ids[:n_train])
    val_set = set(actor_ids[n_train : n_train + n_val])
    test_set = set(actor_ids[n_train + n_val :])

    split_map: dict[str, set[int]] = {
        "train": train_set,
        "val": val_set,
        "test": test_set,
    }
    split_map[split]

    return [(p, label_map[e]) for p, aid, e in samples if aid in split_map[split]]


class CREMADDataset(Dataset):
    def __init__(self, split: str = "train") -> None:
        dset = config.dataset
        feat = config.feature

        for dir in AUDIO_DIRS:
            if os.path.exists(dir):
                self.audio_dir = dir
                break
        else:
            raise ValueError("couldn't find audio dir")

        self.target_sr: int = dset.sample_rate
        self.target_len: int = int(dset.voice_length_seconds * dset.sample_rate)
        self.split: str = split
        self.seed: int = dset.seed
        self.ratios: dict[str, float] = dset.split_ratios
        self.emotion_whitelist: set[str] = set(dset.emotions)
        speaker_count = (
            dset.speakers.get("count", 0) if isinstance(dset.speakers, dict) else 0
        )
        self.max_speakers: int | None = speaker_count if speaker_count > 0 else None

        self.feature_extractor = build_extractor(feat.extractor, config)

        label_map = _build_label_map(self.emotion_whitelist)
        raw = _scan_files(self.audio_dir, self.emotion_whitelist, self.max_speakers)
        self.samples: list[tuple[str, int]] = _compute_split(
            raw, self.split, self.seed, self.ratios, label_map
        )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        path, label = self.samples[index]
        waveform = _load_waveform(path, self.target_sr)
        waveform = _unify_length(waveform, self.target_len)
        features = self.feature_extractor(waveform)
        return {
            "features": features,
            "label": torch.tensor(label, dtype=torch.long),
        }
