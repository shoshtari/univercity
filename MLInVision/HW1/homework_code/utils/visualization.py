import numpy as np
from numpy.typing import NDArray
from models.model import MLP
from data.data_loader import load_data
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


def plot_all(model: MLP, logs: dict):
    """
    plot error, accuracy and confusion matrix for train and val set
    it doesn't do plot show in order to be able to save it
    """

    data = load_data()
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    plt.plot([i["train error"] for i in logs], label="train", lw=3, alpha=0.7)
    plt.plot([i["val error"] for i in logs], label="val", lw=3, alpha=0.7)
    plt.title("error")
    plt.xlabel("Epoch")
    plt.ylabel("Error")
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot([i["train accuracy"] for i in logs], label="train", lw=3, alpha=0.7)
    plt.plot([i["val accuracy"] for i in logs], label="val", lw=3, alpha=0.7)
    plt.title("Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.subplot(2, 2, 3)
    plot_confusion_matrix(
        y_pred=model.predict(data.X_train),
        y_true=np.argmax(data.y_train, axis=1),
        normalize=False,
    )
    plt.title("Train confusion matrix")

    plt.subplot(2, 2, 4)
    plot_confusion_matrix(
        y_pred=model.predict(data.X_val),
        y_true=np.argmax(data.y_val, axis=1),
        normalize=False,
    )
    plt.title("Validation confusion matrix")
