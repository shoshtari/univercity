import numpy as np
from numpy.typing import NDArray
from models.layer.activation.abstract import ActivationFunction


class Relu(ActivationFunction):

    def forward(self, inputs: NDArray[np.float64]) -> NDArray[np.float64]:
        self._inputs = inputs
        ans = inputs.copy()
        ans[inputs < 0] = 0
        return ans

    def backward(self) -> NDArray[np.float64]:
        ans = np.ones(shape=self._inputs.shape)
        ans[self._inputs < 0] = 0
        delattr(self, "_inputs")
        return ans
