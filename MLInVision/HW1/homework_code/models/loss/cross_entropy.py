import numpy as np
from numpy.typing import NDArray
from models.loss.abstract import AbstractLossFunction


class CrossEntropyLoss(AbstractLossFunction):
    """
    note that in derivative it return dL/dz not dL/da
    """

    def __init__(self, C: int, eps: float = 1e-8):
        """
        eps is normalizing factor to avoid log 0
        """
        self.eps = eps
        self.C = C

    def calculate_loss(self, preds, actuals):
        assert preds.shape == actuals.shape, "preds and actual must have the same shape"
        assert preds.shape[1] == self.C

        self.deriv = preds - actuals

        preds = np.clip(preds, self.eps, 1 - self.eps)

        # sum actuals log(preds)
        loss = np.mean((-actuals * np.log(preds)).sum(axis=1))
        return loss

    def calculate_derivative(self) -> NDArray[np.float64]:
        ans = self.deriv
        delattr(self, "deriv")
        return ans
