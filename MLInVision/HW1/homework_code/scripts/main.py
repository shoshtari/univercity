from data import load_data
import matplotlib.pyplot as plt
import numpy as np
from models.layer.initializer import Initializer
from models.layer.activation import Relu, Softmax
from scripts.train import create_and_train_model_from_config
from config.config import Config
from utils import plot_all

if __name__ == "__main__":
    data = load_data()
    model, logs = create_and_train_model_from_config(
        Config.read_yaml(), return_logs=True
    )

    plot_all(model, logs)
    plt.show()
