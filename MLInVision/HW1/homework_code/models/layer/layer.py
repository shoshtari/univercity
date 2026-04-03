import numpy as np
from numpy.typing import NDArray
from typing import Literal, Sequence
from models.layer.activation import ActivationFunction, Relu, Softmax
from models.layer.initializer import InitializerFn, Initializer
from dataclasses import dataclass


@dataclass
class BackpropData:
    """
    needed data to propagate from next layer to before
    """

    delta: NDArray[np.float64]
    W: NDArray[np.float64]


class Layer:

    def __init__(
        self,
        layer_size: int,
        previous_layer_size: int,
        learning_rate: float,
        momentum: float,
        activation: ActivationFunction,
        W_initializer: InitializerFn,
        b_initializer: InitializerFn,
        regularization_factor: float,
    ):
        self.activation = activation
        self.regularization_factor = regularization_factor

        # parameter initializiation
        self.W = W_initializer((layer_size, previous_layer_size))
        self.b = b_initializer((layer_size,))

        # optimizer initialization
        self.v_w = np.zeros(shape=self.W.shape)
        self.v_b = np.zeros(shape=self.b.shape)
        self.learning_rate = learning_rate
        self.momentum = momentum

    @property
    def size(self):
        return len(self.W)

    @property
    def previous_size(self):
        return self.W.shape[1]

    def forward(self, inputs: NDArray[np.float64]) -> NDArray[np.float64]:
        self.Z = np.dot(inputs, self.W.T) + self.b
        self.A = self.activation.forward(self.Z)
        self._inputs = inputs
        return self.A

    def backward(
        self,
        next_layer_data: BackpropData | None,
        deriv_a: NDArray[np.float64] | None = None,  # for output layer
        skip_activation: bool = False,
    ) -> BackpropData:

        # deriv to a
        # Delta Symbol - Δ
        # δ_{i + 1}: n * (n_{i + 1})
        # a: n * n_i
        # W_{i}: n_{i} * n_{i - 1}
        # Z_i: n * n_i
        # z_{i + 1} = a * W_{i + 1}^T
        if deriv_a is None:
            assert (
                next_layer_data is not None
            ), "need next layer data (for output layer, you can provide deriv_a)"
            deriv_a = np.dot(next_layer_data.delta, next_layer_data.W)

        if skip_activation:
            delta = deriv_a
        else:
            o = self.activation.backward()
            delta = o * deriv_a
        deriv_w = np.dot(delta.T, self._inputs)  # dot of self.w and self._inputs
        deriv_b = np.sum(delta, axis=0)
        batch_size = self._inputs.shape[0]
        deriv_w = deriv_w / batch_size
        deriv_b = deriv_b / batch_size
        deriv_w = deriv_w + 2 * self.regularization_factor * self.W

        return_data = BackpropData(delta=delta, W=self.W)
        self.v_w = self.momentum * self.v_w - self.learning_rate * deriv_w
        self.v_b = self.momentum * self.v_b - self.learning_rate * deriv_b
        np.clip(self.v_w, -5.0, 5.0, out=self.v_w)
        np.clip(self.v_b, -5.0, 5.0, out=self.v_b)
        self.W += self.v_w
        self.b += self.v_b
        delattr(self, "_inputs")
        return return_data

    @staticmethod
    def get_layers(
        hidden_layer_sizes: Sequence[int],
        momentum: float,
        learning_rate: float,
        regularization_factor: float,
        input_size: int = 784,
        output_size: int = 10,
    ):
        W_initializer = Initializer.standard_normal
        b_initializer = Initializer.zero
        previous = input_size
        layers = []
        for layer_size in hidden_layer_sizes:
            layers.append(
                Layer(
                    W_initializer=W_initializer,
                    b_initializer=b_initializer,
                    layer_size=layer_size,
                    momentum=momentum,
                    learning_rate=learning_rate,
                    previous_layer_size=previous,
                    activation=Relu(),
                    regularization_factor=regularization_factor,
                )
            )
            previous = layer_size

        layers.append(
            Layer(
                W_initializer=W_initializer,
                b_initializer=b_initializer,
                layer_size=output_size,
                previous_layer_size=previous,
                activation=Softmax(),
                momentum=momentum,
                learning_rate=learning_rate,
                regularization_factor=regularization_factor,
            )
        )
        return layers
