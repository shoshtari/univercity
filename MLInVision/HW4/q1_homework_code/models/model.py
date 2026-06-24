from __future__ import annotations

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from models.vocab import Vocab

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"
IGNORE_INDEX = -100


def _vocab_id(vocab: Vocab, token: str) -> int:
    return vocab._token_to_id.get(token, vocab._token_to_id.get(UNK_TOKEN, 0))


def _prepare_batch(
    batch: list,
    vocab: Vocab,
    tag_key: str,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    token_ids: list[list[int]] = []
    label_ids: list[list[int]] = []
    lengths: list[int] = []

    for tokens, tags_dict in batch:
        tags = tags_dict[tag_key]
        length = sum(1 for token in tokens if token != PAD_TOKEN)
        lengths.append(length)
        token_ids.append([
            vocab.token_to_id(token) 
            for token in tokens
        ])
        label_ids.append(
            [IGNORE_INDEX if tag == PAD_TOKEN else vocab.tag_to_id(tag) for tag in tags]
        )

    input_ids = torch.tensor(token_ids, device=device)
    labels = torch.tensor(label_ids, device=device)
    for i, length in enumerate(lengths):
        labels[i, length:] = IGNORE_INDEX

    return input_ids, labels, torch.tensor(lengths, device=device)


class Tagger(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        pad_idx: int,
        embed_dim: int,
        hidden_dim: int,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.hidden = None
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        if self.hidden is None:
            raise ValueError("hidden layer is not specified")
        embedded = self.embedding(input_ids)
        output, _ = self.hidden(embedded)
        return self.fc(output)


class BiRNNTagger(Tagger):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embed_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        pad_idx: int,
    ) -> None:
        super().__init__(
            embed_dim=embed_dim,
            hidden_dim=hidden_dim,
            pad_idx=pad_idx,
            vocab_size=vocab_size,
            num_classes=num_classes,
        )
        self.hidden = nn.RNN(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )


class BiLSTMTagger(Tagger):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embed_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        pad_idx: int,
    ) -> None:
        super().__init__(
            embed_dim=embed_dim,
            hidden_dim=hidden_dim,
            pad_idx=pad_idx,
            vocab_size=vocab_size,
            num_classes=num_classes,
        )
        self.hidden = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )


class BiGRUTagger(Tagger):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embed_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        pad_idx: int,
    ) -> None:
        super().__init__(
            embed_dim=embed_dim,
            hidden_dim=hidden_dim,
            pad_idx=pad_idx,
            vocab_size=vocab_size,
            num_classes=num_classes,
        )
        self.hidden = nn.GRU(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
