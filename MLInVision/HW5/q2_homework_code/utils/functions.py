import numpy as np
import torch


def rosenbrock(x, y):
    return 100 * (y - x**2) ** 2 + (1 - x) ** 2


def rosenbrock_grad_x(x, y):
    return 400 * x * (x**2 - y) + 2 * (x - 1)


def rosenbrock_grad_y(x, y):
    return 200 * (y - x**2)


