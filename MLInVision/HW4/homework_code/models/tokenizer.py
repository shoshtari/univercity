"""
the dataset is tokenized. but we want to build vocab an assign id, this script does that.
"""
from torch.utils.data import Dataset

def build_vocab(ds: Dataset) -> tuple[list[str], dict[str, int],]:
    """
    return the vocab and token to id dictionary
    """
    for row in ds:
