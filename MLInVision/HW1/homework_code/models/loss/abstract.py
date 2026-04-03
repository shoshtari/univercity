from abc import ABC, abstractmethod
from numpy.typing import NDArray
import numpy as np


class AbstractLossFunction(ABC):

    @abstractmethod
    def calculate_loss(
        self, preds: NDArray[np.float64], actuals: NDArray[np.float64]
    ) -> float:
        raise NotImplementedError

    @abstractmethod
    def calculate_derivative(self) -> NDArray[np.float64]:
        raise NotImplementedError
