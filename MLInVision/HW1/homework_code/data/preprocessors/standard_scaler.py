from data.preprocessors.abstract import AbstractPreprocessor


class StandardScaler(AbstractPreprocessor):
    def fit(self, X):
        self._mean = X.mean(axis=0)
        self._std = X.std(axis=0)
        self._std[self._std == 0] = 1

    def transform(self, X):
        return (X - self._mean) / self._std
