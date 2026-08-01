import torch

from utils.functions import rosenbrock


def run_optimization(
    optimizer_cls,
    lr,
    initial_point,
    optimal_point,
    gradient_threshold,
    max_iterations=10000,
):
    x = torch.tensor([initial_point[0]], requires_grad=True)
    y = torch.tensor([initial_point[1]], requires_grad=True)
    opt = optimizer_cls([x, y], lr=lr)

    history = {
        "loss": [],
        "distance": [],
        "path": [],
        "iterations": 0,
        "converged": False,
        "diverged": False,
    }

    for step in range(max_iterations):
        opt.zero_grad()
        loss = rosenbrock(x, y)
        loss.backward()

        gx = x.grad if x.grad is not None else torch.zeros(1)
        gy = y.grad if y.grad is not None else torch.zeros(1)
        grad_norm = torch.norm(torch.stack([gx, gy]))

        loss_val = loss.item()
        distance_val = torch.dist(
            torch.stack([x, y]), torch.tensor(optimal_point)
        ).item()

        if (
            not torch.isfinite(loss)
            or not torch.isfinite(torch.tensor([distance_val, grad_norm])).all()
        ):
            history["diverged"] = True
            break

        history["loss"].append(loss_val)
        history["distance"].append(distance_val)
        history["path"].append((x.item(), y.item()))
        history["iterations"] = step + 1

        if grad_norm < gradient_threshold:
            history["converged"] = True
            break

        opt.step()

    return history
