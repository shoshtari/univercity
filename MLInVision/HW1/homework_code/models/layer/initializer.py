from typing import Callable
import numpy as np
from numpy.typing import NDArray
from typing import TypeAlias

InitializerFn: TypeAlias = Callable[[tuple[int, ...]], NDArray[np.float64]]


class Initializer:
    @staticmethod
    def standard_normal(shape: tuple) -> NDArray[np.float64]:
        return np.random.randn(*shape)

    @staticmethod
    def zero(shape: tuple) -> NDArray[np.float64]:
        return np.zeros(shape)

    @classmethod
    def xavier(cls, shape: tuple) -> NDArray[np.float64]:
        """
        aka gloroot
        """
        fan_out, fan_in = shape
        return cls.standard_normal(shape) * np.sqrt(2 / (fan_in + fan_out))

    @classmethod
    def he(cls, shape: tuple) -> NDArray[np.float64]:
        """
        aka Kaiming
        """
        _, fan_in = shape
        return cls.standard_normal(shape) * np.sqrt(2.0 / fan_in)

    @classmethod
    def constant(cls, constant: float) -> Callable[[tuple], NDArray[np.float64]]:
        def inner(shape: tuple):
            return cls.zero(shape) + constant

        return inner

    @classmethod
    def normal(cls, mean: float, std: float) -> Callable[[tuple], NDArray[np.float64]]:
        def inner(shape: tuple):
            ans = cls.standard_normal(shape)
            ans *= std
            ans += mean
            return ans

        return inner
