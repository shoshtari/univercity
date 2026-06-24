"""
the dataset is tokenized. but we want to build vocab an assign id, this script does that.
"""

from torch.utils.data import Dataset


class Vocab:
    def __init__(self, ds: Dataset, cutoff: int = 5, tag_key: str = "ner_tags") -> None:
        tokens_to_add = (
            "<unk>",
            "<pad>",
            "<s>",
            "</s>",
        )
        self.tokens: list[str] = []
        self._token_to_id: dict[str, int] = {}
        self._tag_to_id: dict[str, int] = {}
        counts: dict[str, int] = {}

        for row in ds:
            for token in row[0]:
                counts[token] = counts.get(token, 0) + 1
                if counts[token] == cutoff:
                    self._token_to_id[token] = len(self.tokens)
                    self.tokens.append(token)

            for tag in row[1][tag_key]:
                if tag not in self._tag_to_id:
                    self._tag_to_id[tag] = len(self._tag_to_id)

        for token in tokens_to_add:
            if counts.get(token, 0) >= cutoff:
                # it is in the vocab already
                continue
            self._token_to_id[token] = len(self.tokens)
            self.tokens.append(token)

    def id_to_token(self, idx: int) -> str:
        return self.tokens[idx]

    def token_to_id(self, token: str) -> int:
        if token not in self._token_to_id:
            token = "<unk>"
        return self._token_to_id[token]

    def tag_to_id(self, tag: str) -> int:
        return self._tag_to_id[tag]

    def id_to_tag(self, idx: int) -> str:
        for tag, tag_id in self._tag_to_id.items():
            if tag_id == idx:
                return tag
        raise KeyError(idx)

    def num_tags(self) -> int:
        return len(self._tag_to_id)

    def __len__(self) -> int:
        return len(self.tokens)
