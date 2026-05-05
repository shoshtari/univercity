from typing import Literal
import os
import numpy as np

from torch.utils.data import Dataset, DataLoader
import pickle
import cv2

class Augmenter:
    p = 0.2
    noise_p = 0.02
    def __init__(self, is_train: bool = True):
        self.is_train = is_train

    def __call__(self, img: np.ndarray) -> np.array:
        if self.is_train:
            # rotate
            h, w = img.shape[-2:]
            if np.random.rand() < self.p:
                angle = np.random.uniform(-10, 10)
                M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
                
                if img.ndim == 3:
                    for c in range(img.shape[0]):
                        img[c] = cv2.warpAffine(img[c], M, (w, h))
                else:
                    img = cv2.warpAffine(img, M, (w, h))
            if np.random.rand() < self.p:

                tx = np.random.uniform(-2, 2)
                ty = np.random.uniform(-2, 2)
                T = np.float32([[1, 0, tx], [0, 1, ty]])
                
                if img.ndim == 3:
                    for c in range(img.shape[0]):
                        img[c] = cv2.warpAffine(img[c], T, (w, h))
                else:
                    img = cv2.warpAffine(img, T, (w, h))
            if np.random.rand() < self.noise_p:
                if img.ndim == 3:
                    for c in range(img.shape[0]):
                        img[c] = cv2.GaussianBlur(img[c], (3, 3), 0)
                else:
                    img = cv2.GaussianBlur(img, (3, 3), 0)

        if img.max() > 1.0:
            img = img/ 255.0
            
        return img

class MNISTDataset(Dataset):
    DATASET_PATHS = (

    "./data/dataset/mnist.pkl",
     "../data/dataset/mnist.pkl"
    )

    def __init__(self, data_type: Literal["train", "val", "test"]):
        for path in self.DATASET_PATHS:
            if not os.path.exists(path):
                continue
            with open(path, "rb") as f:
                data = pickle.load(f, encoding="latin1")
                break

        match data_type:
            case "train":
                data = data[0]
            case "val":
                data = data[1]
            case "test":
                data = data[2]
            case _:
                raise ValueError(
                    "Invalid data type. Expected 'train', 'val', or 'test'."
                )

        images = data[0]
        labels = data[1]
        images = images.reshape(len(data[0]), 28, 28)
        images = np.stack([images, images, images], axis=1)

        self._X = images
        self._y = labels # TODO: one-hot may help. but without it I got good results.
        if len(self._X) != len(self._y):
            raise ValueError("Inconsistent data lengths.")
        self.augmenter = Augmenter(is_train=(data_type == "train"))

    def __len__(self):
        return len(self._X)

    def __getitem__(self, idx):
        img, label = self._X[idx], self._y[idx]
        img = self.augmenter(img)
        return img, label


class FashionMNISTDataset(Dataset):
    DATASET_PATHES = (
        "./data/dataset",
        "../data/dataset"
    )

    def __init__(self, data_type: Literal["train", "val", "test"]):

        if data_type not in ["train", "val", "test"]:
            raise ValueError("Invalid data type. Expected 'train', 'val', or 'test'.")

        for path in self.DATASET_PATHES:
            if not os.path.exists(path):
                continue
            dir_path = path
            break
        else:
            raise FileNotFoundError("No valid dataset path found.")

        path_suffix = "train" if data_type in ("train", "val") else "t10k"
        labels_path = os.path.join(dir_path, "%s-labels-idx1-ubyte" % path_suffix)
        images_path = os.path.join(dir_path, "%s-images-idx3-ubyte" % path_suffix)

        with open(labels_path, "rb") as lbpath:
            labels = np.frombuffer(lbpath.read(), dtype=np.uint8, offset=8)

        with open(images_path, "rb") as imgpath:
            images = np.frombuffer(imgpath.read(), dtype=np.uint8, offset=16).reshape(
                len(labels), 784
            )
        if len(images) != len(labels):
            raise ValueError("Inconsistent data lengths.")
        
        if data_type in ("val", "train"):
            np.random.seed(42)
            indices = np.random.choice(len(images), 1000, replace=False)
            if data_type == "train":
                indices = ~indices

            images = images[indices]
            labels = labels[indices]

        images = images.reshape(len(images), 28, 28)
        images = np.stack([images, images, images], axis=1)

        self._X = images
        self._y = labels
        self._X = self._X.astype(np.float32)
        self._y = self._y.astype(np.int64)
        self.augmenter = Augmenter(is_train=(data_type == "train"))

    def __len__(self):
        return len(self._X)

    def __getitem__(self, idx):
        image, label = self._X[idx], self._y[idx]
        image = self.augmenter(image)
        return image, label


def get_dataloader(dataset: Dataset, batch_size: int = 32, shuffle: bool = True):
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
