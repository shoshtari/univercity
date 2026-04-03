import os
import numpy as np
import pickle
from data.dtos import LoadDataOutput
from cachetools import cached

DATASET_PATHS = (
    # Since the given dataset showed deprecation warning on align
    # I repickled to a new pickle file
    "../data/dataset/mnist.pkl.new",
    "./data/dataset/mnist.pkl.new",
    "../data/dataset/mnist.pkl.original",
    "./data/dataset/mnist.pkl.original",
    "../data/dataset/mnist.pkl",
    "./data/dataset/mnist.pkl",
)


@cached({})
def load_data():

    path = None
    for possible_path in DATASET_PATHS:
        if os.path.exists(possible_path):
            path = possible_path
            break
    assert path is not None, "Couldn't find dataset in all possible PATHS"

    with open(path, "rb") as f:
        data = pickle.load(f, encoding="latin1")

    return LoadDataOutput(
        X_train=data[0][0],
        y_train=np.eye(10)[data[0][1]],
        X_val=data[1][0],
        y_val=np.eye(10)[data[1][1]],
        X_test=data[2][0],
        y_test=np.eye(10)[data[2][1]],
    )


if __name__ == "__main__":
    print(load_data().y_train)
