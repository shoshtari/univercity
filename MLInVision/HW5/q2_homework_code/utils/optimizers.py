import torch


class SGD(torch.optim.Optimizer):
    def __init__(self, params, lr=0.01):
        super().__init__(params, {"lr": lr})

    @torch.no_grad()
    def step(self, closure=None):
        loss = None

        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group["lr"]

            for p in group["params"]:
                if p.grad is not None:
                    p.add_(p.grad, alpha=-lr)

        return loss


class RMSProp(torch.optim.Optimizer):
    def __init__(self, params, lr=0.01, alpha=0.99, eps=1e-8):
        super().__init__(
            params,
            {"lr": lr, "alpha": alpha, "eps": eps},
        )

    @torch.no_grad()
    def step(self, closure=None):
        loss = None

        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group["lr"]
            alpha = group["alpha"]
            eps = group["eps"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                g = p.grad
                state = self.state[p]

                if not state:
                    state["avg"] = torch.zeros_like(p)

                avg = state["avg"]
                avg.mul_(alpha).addcmul_(g, g, value=1 - alpha)

                p.addcdiv_(g, avg.sqrt().add_(eps), value=-lr)

        return loss


class Adam(torch.optim.Optimizer):
    def __init__(
        self,
        params,
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
    ):
        super().__init__(
            params,
            {"lr": lr, "betas": betas, "eps": eps},
        )

    @torch.no_grad()
    def step(self, closure=None):
        loss = None

        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            lr = group["lr"]
            b1, b2 = group["betas"]
            eps = group["eps"]

            for p in group["params"]:
                if p.grad is None:
                    continue

                g = p.grad
                state = self.state[p]

                if not state:
                    state["t"] = 0
                    state["m"] = torch.zeros_like(p)
                    state["v"] = torch.zeros_like(p)

                state["t"] += 1

                t = state["t"]
                m = state["m"]
                v = state["v"]

                m.mul_(b1).add_(g, alpha=1 - b1)
                v.mul_(b2).addcmul_(g, g, value=1 - b2)

                m_hat = m / (1 - b1**t)
                v_hat = v / (1 - b2**t)

                p.addcdiv_(m_hat, v_hat.sqrt().add_(eps), value=-lr)

        return loss