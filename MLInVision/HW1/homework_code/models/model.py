import numpy as np
from numpy.typing import NDArray
from models.layer import Layer
from models.loss import CrossEntropyLoss, AbstractLossFunction
from typing import Sequence, Literal, Optional


class MLP:
    def __init__(
        self,
        layers: Sequence[Layer],
        loss: str,
        early_stopping_threshold: int,
        normalize_input: bool = False,
    ):
        self.early_stopping_threshold = early_stopping_threshold
        self.skip_activation_in_output = False
        for i in range(1, len(layers)):
            assert (
                layers[i - 1].size == layers[i].previous_size
            ), f"Layer {i - 1} and {i} size mismatch"
        self.layers: Sequence[Layer] = layers
        self.loss_function: AbstractLossFunction
        self.normalize_input = normalize_input
        match loss:
            # case "mse":
            #     self.loss_function = MSELoss()
            case "cross_entropy":
                self.loss_function = CrossEntropyLoss(C=layers[-1].size)
                self.skip_activation_in_output = True
            case _:
                raise ValueError(f"Unknown error {loss}")

    def _validate(self, X: NDArray[np.float64], y: Optional[NDArray[np.float64]]):
        assert len(X.shape) == 2, "X shape is not ok"
        assert (
            X.shape[1] == self.layers[0].previous_size
        ), "features and first layer doesn't match"

        if y is None:
            return

        assert len(y.shape) == 2, "y shape is not ok"
        assert X.shape[0] == y.shape[0], "X and y has different number of rows"
        assert (
            y.shape[1] == self.layers[-1].size
        ), f"Y must be one hot encoded and match the final layer size {y.shape[1] = }, {self.layers[-1].size=}"

    def forward(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def backward(self, error_derivative: NDArray[np.float64]):
        layer_data = self.layers[-1].backward(
            next_layer_data=None,
            deriv_a=error_derivative,
            skip_activation=self.skip_activation_in_output,
        )

        for layer in reversed(self.layers[:-1]):
            layer_data = layer.backward(
                next_layer_data=layer_data,
            )

    def fit(
        self,
        X_train: NDArray[np.float64],
        y_train: NDArray[np.float64],
        epochs: int,
        batch_size: int,
        X_val: Optional[NDArray[np.float64]],
        y_val: Optional[NDArray[np.float64]],
        logging_step=10,
        logging_enable_print=True,
    ):
        if self.normalize_input:
            self.X_mean = X_train.mean(axis=0)
            self.X_std = X_train.std(axis=0)
            self.X_std[self.X_std == 0] = 1
            X_train = (X_train - self.X_mean) / self.X_std

        self._validate(X=X_train, y=y_train)
        if batch_size is None:
            batch_size = len(X_train)
        logs = []

        best_val_acc = 0.0
        val_decline = 0
        for i in range(epochs):
            for j in range(0, len(X_train), batch_size):
                X_batch = X_train[j : j + batch_size]
                Y_batch = y_train[j : j + batch_size]

                train_preds = self.forward(X_batch)
                self.loss_function.calculate_loss(preds=train_preds, actuals=Y_batch)
                self.backward(
                    error_derivative=self.loss_function.calculate_derivative()
                )
            # log acquiring
            train_preds = self.forward(X_train)
            train_error = self.loss_function.calculate_loss(
                preds=train_preds, actuals=y_train
            )
            train_accuracy = np.count_nonzero(
                np.argmax(train_preds, axis=1) == np.argmax(y_train, axis=1)
            ) / len(X_train)

            log_data = {
                "epoch": i,
                "train error": train_error,
                "train accuracy": train_accuracy,
            }
            if X_val is not None and y_val is not None:
                if self.normalize_input:
                    val_preds = self.forward((X_val - self.X_mean) / self.X_std)
                else:
                    val_preds = self.forward(X_val)
                val_error = self.loss_function.calculate_loss(
                    preds=val_preds, actuals=y_val
                )
                val_accuracy = np.count_nonzero(
                    np.argmax(val_preds, axis=1) == np.argmax(y_val, axis=1)
                ) / len(X_val)
                log_data |= {
                    "val error": val_error,
                    "val accuracy": val_accuracy,
                }

                if self.early_stopping_threshold:
                    if val_accuracy > best_val_acc:
                        best_val_acc = val_accuracy
                        val_decline = 0
                    else:
                        val_decline += 1
                        if val_decline > self.early_stopping_threshold:
                            return logs
            logs.append(log_data)
            if logging_step and i % logging_step == 0 and logging_enable_print:
                print(log_data)
        return logs

    def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        if self.normalize_input:
            X = (X - self.X_mean) / self.X_std
        preds = self.forward(X)
        return np.argmax(preds, axis=1)

    def evaluate(self, X: NDArray[np.float64], y: NDArray[np.float64]):
        preds = self.predict(X)
        if len(y.shape) == 2:
            y = np.argmax(y, axis=1)
        assert (
            preds.shape == y.shape
        ), f"pred and y shape don't match. {preds.shape=}, {y.shape=}"

        correct = np.count_nonzero(
            preds == y,
        )
        return correct / len(y)
