from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

FIGURE_DIRECTORY = Path("report/pics")


class HodgkinHuxley:
    def __init__(
        self, C=1.0, g_Na=120.0, g_K=36.0, g_L=0.3, E_Na=50.0, E_K=-77.0, E_L=-54.4
    ):
        self.C = C
        self.g_Na = g_Na
        self.g_K = g_K
        self.g_L = g_L
        self.E_Na = E_Na
        self.E_K = E_K
        self.E_L = E_L

    def alpha_n(self, V):
        return 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10))

    def beta_n(self, V):
        return 0.125 * np.exp(-(V + 65) / 80)

    def alpha_m(self, V):
        return 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10))

    def beta_m(self, V):
        return 4.0 * np.exp(-(V + 65) / 18)

    def alpha_h(self, V):
        return 0.07 * np.exp(-(V + 65) / 20)

    def beta_h(self, V):
        return 1.0 / (1 + np.exp(-(V + 35) / 10))

    def m_inf(self, V):
        return self.alpha_m(V) / (self.alpha_m(V) + self.beta_m(V))

    def h_inf(self, V):
        return self.alpha_h(V) / (self.alpha_h(V) + self.beta_h(V))

    def n_inf(self, V):
        return self.alpha_n(V) / (self.alpha_n(V) + self.beta_n(V))

    def derivatives(self, t, state, current):
        V, n, m, h = state
        I_Na = self.g_Na * m**3 * h * (V - self.E_Na)
        I_K = self.g_K * n**4 * (V - self.E_K)
        I_L = self.g_L * (V - self.E_L)
        dVdt = (current - I_Na - I_K - I_L) / self.C
        dndt = self.alpha_n(V) * (1 - n) - self.beta_n(V) * n
        dmdt = self.alpha_m(V) * (1 - m) - self.beta_m(V) * m
        dhdt = self.alpha_h(V) * (1 - h) - self.beta_h(V) * h
        return [dVdt, dndt, dmdt, dhdt]


def simulate_hh(model, current_function, time_span, initial_state, time=None):
    if time is None:
        time = np.linspace(time_span[0], time_span[1], 10000)

    return solve_ivp(
        lambda t, state: model.derivatives(t, state, current_function(t)),
        time_span,
        initial_state,
        t_eval=time,
        method="RK45",
        rtol=1e-6,
        atol=1e-8,
    )


def save_figure(figure, filename):
    FIGURE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    path = FIGURE_DIRECTORY / filename
    figure.tight_layout()
    figure.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(figure)
    print(f"Saved figure: {path}")


def style_axes(axes, xlabel, ylabel, title=None, grid_alpha=0.3):
    axes.set(xlabel=xlabel, ylabel=ylabel)
    if title:
        axes.set_title(title)
    axes.grid(alpha=grid_alpha)


def plot_trace(axes, time, values, *, label=None, color="b", style="-", linewidth=2):
    axes.plot(
        time, values, color=color, linestyle=style, linewidth=linewidth, label=label
    )
