from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray


@dataclass
class LoadDataOutput:
    X_train: NDArray[np.float64]
    y_train: NDArray[np.float64]
    X_val: NDArray[np.float64]
    y_val: NDArray[np.float64]
    X_test: NDArray[np.float64]
    y_test: NDArray[np.float64]
