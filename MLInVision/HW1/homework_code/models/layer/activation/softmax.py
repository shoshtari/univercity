import numpy as np
from numpy.typing import NDArray
from models.layer.activation.abstract import ActivationFunction


class Softmax(ActivationFunction):
    def __init__(self, clip_threshold: int = 50):
        self.clip_threshold = clip_threshold

    def forward(self, inputs: NDArray[np.float64]) -> NDArray[np.float64]:
        inputs = inputs - np.max(inputs, axis=1, keepdims=True)
        inputs = np.clip(inputs, -1 * self.clip_threshold, self.clip_threshold)
        exp_z = np.exp(inputs)
        ans = exp_z / np.sum(exp_z, axis=1, keepdims=True)
        assert ans.shape == inputs.shape
        return ans

    def backward(self) -> NDArray[np.float64]:
        # since we use softmax only at last layer with CE loss
        # the gradient is calculated directly (dL/dz not dL/dz * dz/da)
        # so backward is not needed
        raise NotImplementedError
