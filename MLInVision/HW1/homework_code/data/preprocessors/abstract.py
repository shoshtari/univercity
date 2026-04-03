from abc import ABC, abstractmethod
from numpy.typing import NDArray
import numpy as np


class AbstractPreprocessor(ABC):
    def fit(self, data: NDArray[np.float64]):
        raise NotImplementedError

    def transform(self, data: NDArray[np.float64]) -> np.float64:
        raise NotImplementedError

    def fit_transform(self, data: NDArray[np.float64]) -> np.float64:
        self.fit(data)
        return self.transform(data)
