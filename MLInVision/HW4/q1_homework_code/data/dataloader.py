from data.dataset import Conll2003Dataset
import torch
from torch.utils.data import DataLoader


def collate_fn(batch):
    pad_token = "<pad>"
    max_length = max(len(item[0]) for item in batch)
    new_batch = []
    for item in batch:
        new_item = (
            item[0] + [pad_token] * (max_length - len(item[0])),
            {
                "pos_tags": item[1]["pos_tags"]
                + [pad_token] * (max_length - len(item[1]["pos_tags"])),
                "chunk_tags": item[1]["chunk_tags"]
                + [pad_token] * (max_length - len(item[1]["chunk_tags"])),
                "ner_tags": item[1]["ner_tags"]
                + [pad_token] * (max_length - len(item[1]["ner_tags"])),
            },
        )
        new_batch.append(new_item)
    return new_batch


def get_dataloader(ds: Conll2003Dataset, batch_size: int = 32) -> DataLoader:
    torch.manual_seed(42)
    return DataLoader(ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
