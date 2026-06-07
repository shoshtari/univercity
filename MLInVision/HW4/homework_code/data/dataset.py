# coding=utf-8


import os

import datasets
from torch.utils.data import Dataset

logger = datasets.logging.get_logger(__name__)


datadirs = (
    "./data/dataset/conll2003",
    "../data/dataset/conll2003",
)


def _read_file(segment: str):
    """
    This code is mainly copied from conll2003 hugging face dataset
    since hf deprecated code running, i copied what i needed from it and downloaded dataset manually
    """
    for datadir in datadirs:
        filepath = os.path.join(datadir, f"{segment}.txt")
        if os.path.exists(filepath):
            break
    else:
        raise ValueError(f"couldn't file data for segemnt {segment}")
    logger.info("⏳ Generating examples from = %s", filepath)
    with open(filepath, encoding="utf-8") as f:
        guid = 0
        tokens = []
        pos_tags = []
        chunk_tags = []
        ner_tags = []
        for line in f:
            if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                if tokens:
                    yield (
                        guid,
                        {
                            "id": str(guid),
                            "tokens": tokens,
                            "pos_tags": pos_tags,
                            "chunk_tags": chunk_tags,
                            "ner_tags": ner_tags,
                        },
                    )
                    guid += 1
                    tokens = []
                    pos_tags = []
                    chunk_tags = []
                    ner_tags = []
            else:
                # conll2003 tokens are space separated
                splits = line.split(" ")
                tokens.append(splits[0])
                pos_tags.append(splits[1])
                chunk_tags.append(splits[2])
                ner_tags.append(splits[3].rstrip())
        # last example
        if tokens:
            yield (
                guid,
                {
                    "id": str(guid),
                    "tokens": tokens,
                    "pos_tags": pos_tags,
                    "chunk_tags": chunk_tags,
                    "ner_tags": ner_tags,
                },
            )


class Conll2003Dataset(Dataset):
    def __init__(self, segment: str) -> None:
        super().__init__()
        self.samples = self._read_samples(segment)

    @staticmethod
    def _read_samples(segment: str):
        gen = _read_file(segment)
        ans = []
        for entry in gen:
            ans.append(entry)
        return ans

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index][1]
