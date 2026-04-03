import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod


class ActivationFunction(ABC):
    @abstractmethod
    def forward(self, inputs: NDArray[np.float64]) -> NDArray[np.float64]:
        raise NotImplementedError

    @abstractmethod
    def backward(self) -> NDArray[np.float64]:
        raise NotImplementedError
