
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt

def plot_confusion_matrix(
    y_true: NDArray[np.number], y_pred: NDArray[np.number], normalize: bool = True
):
    cm = np.zeros((10, 10), dtype=int)

    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    if normalize:
        cm = cm / cm.sum()

    plt.imshow(cm, cmap="Blues")
    plt.colorbar()
    plt.xlabel("Predicted label")
    plt.ylabel("True label")

    plt.xticks(range(10))
    plt.yticks(range(10))

    for i in range(10):
        for j in range(10):
            plt.text(j, i, cm[i, j], ha="center", va="center", fontsize=8)

