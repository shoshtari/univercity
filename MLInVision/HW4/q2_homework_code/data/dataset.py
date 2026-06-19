import torch
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import Subset

transform_train = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

VAL_SPLIT = 0.1
SPLIT_SEED = 42

_train_full = torchvision.datasets.CIFAR10(
    root='./data',
    train=True,
    download=True,
    transform=transform_train,
)
_val_full = torchvision.datasets.CIFAR10(
    root='./data',
    train=True,
    download=True,
    transform=transform_test,
)


def make_train_val_indices(num_samples, val_split=VAL_SPLIT, seed=SPLIT_SEED):
    generator = torch.Generator().manual_seed(seed)
    permutation = torch.randperm(num_samples, generator=generator).tolist()
    val_size = int(num_samples * val_split)
    val_indices = permutation[:val_size]
    train_indices = permutation[val_size:]
    return train_indices, val_indices


TRAIN_INDICES, VAL_INDICES = make_train_val_indices(len(_train_full))

train_dataset = Subset(_train_full, TRAIN_INDICES)
val_dataset = Subset(_val_full, VAL_INDICES)

test_dataset = torchvision.datasets.CIFAR10(
    root='./data',
    train=False,
    download=True,
    transform=transform_test
)

