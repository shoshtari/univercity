import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, fsolve

from common import HodgkinHuxley, plot_trace, save_figure, simulate_hh, style_axes


class MorrisLecar:
    def __init__(self):
        self.C_m = 1.0
        self.g_Ca = 4.0
        self.g_K = 8.0
        self.g_L = 2.0
        self.V_Ca = 120.0
        self.V_K = -84.0
        self.V_L = -60.0
        self.V1, self.V2 = -1.2, 18.0
        self.V3, self.V4 = 2.0, 30.0
        self.V5, self.V6 = -40.0, 10.0
        self.V7, self.V8 = 0.4, 18.0

    def m_inf(self, V):
        return 0.5 * (1 + np.tanh((V - self.V1) / self.V2))

    def tau_m(self, V):
        return 1 / np.cosh((V - self.V3) / (2 * self.V4))

    def w_inf(self, V):
        return 0.5 * (1 + np.tanh((V - self.V5) / self.V6))

    def tau_w(self, V):
        return 1 / np.cosh((V - self.V7) / (2 * self.V8))

    def derivatives(self, state, current=90.0):
        V, m, w = state
        I_Ca = self.g_Ca * m * (V - self.V_Ca)
        I_K = self.g_K * w * (V - self.V_K)
        I_L = self.g_L * (V - self.V_L)
        dVdt = (current - I_Ca - I_K - I_L) / self.C_m
        dmdt = (self.m_inf(V) - m) / self.tau_m(V)
        dwdt = (self.w_inf(V) - w) / self.tau_w(V)
        return np.array([dVdt, dmdt, dwdt])

    def reduced_derivatives(self, state, current=90.0):
        V, w = state
        I_Ca = self.g_Ca * self.m_inf(V) * (V - self.V_Ca)
        I_K = self.g_K * w * (V - self.V_K)
        I_L = self.g_L * (V - self.V_L)
        dVdt = (current - I_Ca - I_K - I_L) / self.C_m
        dwdt = (self.w_inf(V) - w) / self.tau_w(V)
        return np.array([dVdt, dwdt])


def simulate(model, initial_state, time, current):
    solution = solve_ivp(
        lambda t, state: model.reduced_derivatives(state, current),
        (time[0], time[-1]),
        initial_state,
        t_eval=time,
        rtol=1e-6,
        atol=1e-8,
    )
    return solution.t, solution.y.T


def add_direction_field(
    ax,
    derivative,
    voltage_range,
    activation_range,
    horizontal=4.0,
    vertical=0.04,
    label=None,
):
    V, a = np.meshgrid(
        np.linspace(*voltage_range, 18), np.linspace(*activation_range, 13)
    )
    values = np.array(
        [
            derivative([voltage, activation])
            for voltage, activation in zip(V.ravel(), a.ravel())
        ]
    )
    dV = values[:, 0].reshape(V.shape)
    da = values[:, 1].reshape(a.shape)
    ax.quiver(
        V,
        a,
        horizontal * np.sign(dV),
        vertical * np.sign(da),
        color="0.55",
        alpha=0.65,
        angles="xy",
        scale_units="xy",
        scale=1,
        width=0.0025,
        label=label,
    )


def phase_portrait_comparison():
    time = np.linspace(0, 100, 10000)
    hh = HodgkinHuxley()
    V0 = -65.0
    hh_state = [V0, hh.n_inf(V0), hh.m_inf(V0), hh.h_inf(V0)]
    hh_solution = simulate_hh(hh, lambda t: 10.0, (0, 100), hh_state, time)

    ml = MorrisLecar()
    _, ml_solution = simulate(ml, [-60.0, ml.w_inf(-60.0)], time, 90.0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(hh_solution.y[0], hh_solution.y[1], "b", lw=1)
    style_axes(axes[0], "Voltage V (mV)", "Activation n", "HH")
    axes[1].plot(ml_solution[:, 0], ml_solution[:, 1], "r", lw=1)
    style_axes(axes[1], "Voltage V (mV)", "Activation w", "ML")
    save_figure(fig, "1_phase_portrait.png")


def ml_nullclines():
    model = MorrisLecar()
    current = 90.0
    voltages = np.linspace(-80, 60, 500)

    def voltage_nullcline(V):
        I_Ca = model.g_Ca * model.m_inf(V) * (V - model.V_Ca)
        I_L = model.g_L * (V - model.V_L)
        return (current - I_Ca - I_L) / (model.g_K * (V - model.V_K))

    fig, ax = plt.subplots(figsize=(8, 6))
    add_direction_field(
        ax,
        lambda state: model.reduced_derivatives(state, current),
        (-75, 55),
        (0, 1),
        label="Direction",
    )
    ax.plot(voltages, voltage_nullcline(voltages), "b", label="dV/dt = 0")
    ax.plot(voltages, model.w_inf(voltages), "r", label="dw/dt = 0")
    ax.set_ylim(-0.1, 1.1)
    ax.legend()
    style_axes(ax, "Voltage V (mV)", "Activation w", "ML nullclines")
    save_figure(fig, "2_nullclines.png")


def hh_reduced_derivatives(model, state, current=10.0):
    V, n = state
    m = model.m_inf(V)
    h = 1 - n
    I_Na = model.g_Na * m**3 * h * (V - model.E_Na)
    I_K = model.g_K * n**4 * (V - model.E_K)
    I_L = model.g_L * (V - model.E_L)
    dVdt = (current - I_Na - I_K - I_L) / model.C
    dndt = model.alpha_n(V) * (1 - n) - model.beta_n(V) * n
    return np.array([dVdt, dndt])


def hh_voltage_nullcline(model, voltages, current):
    n_values = np.linspace(0, 1, 301)
    points_V, points_n = [], []
    for V in voltages:
        values = [hh_reduced_derivatives(model, [V, n], current)[0] for n in n_values]
        for left, right, f_left, f_right in zip(
            n_values[:-1], n_values[1:], values[:-1], values[1:]
        ):
            if f_left * f_right < 0:
                root = brentq(
                    lambda n: hh_reduced_derivatives(model, [V, n], current)[0],
                    left,
                    right,
                )
                points_V.append(V)
                points_n.append(root)
    return points_V, points_n


def hh_nullclines():
    model = HodgkinHuxley()
    current = 10.0
    voltages = np.linspace(-80, 50, 500)
    V_null, n_null = hh_voltage_nullcline(model, voltages, current)

    fig, ax = plt.subplots(figsize=(8, 6))
    add_direction_field(
        ax,
        lambda state: hh_reduced_derivatives(model, state, current),
        (-75, 45),
        (0, 1),
        label="Direction",
    )
    ax.scatter(V_null, n_null, s=6, color="b", label="dV/dt = 0")
    ax.plot(voltages, model.n_inf(voltages), "r", label="dn/dt = 0")
    ax.set_ylim(-0.1, 1.1)
    ax.legend()
    style_axes(ax, "Voltage V (mV)", "Activation n", "HH nullclines")
    save_figure(fig, "2_hh_nullclines.png")


def numerical_jacobian(derivative, state, step=1e-6):
    J = np.zeros((len(state), len(state)))
    base = np.asarray(derivative(state))
    for column in range(len(state)):
        shifted = np.asarray(state, dtype=float)
        shifted[column] += step
        J[:, column] = (np.asarray(derivative(shifted)) - base) / step
    return J


def find_equilibria(derivative, guesses):
    equilibria = []
    for guess in guesses:
        solution, _, status, _ = fsolve(derivative, guess, full_output=True)
        if status == 1 and all(
            np.linalg.norm(solution - old) > 1e-3 for old in equilibria
        ):
            equilibria.append(solution)
    return equilibria


def stability(derivative, equilibria, name):
    results = []
    for point in equilibria:
        J = numerical_jacobian(derivative, point)
        eigenvalues = np.linalg.eigvals(J)
        if np.all(eigenvalues.real < 0):
            kind = "Stable"
        elif np.all(eigenvalues.real > 0):
            kind = "Unstable"
        else:
            kind = "Saddle"
        print(f"{name} equilibrium: {point}")
        print(f"  Jacobian:\n{J}")
        print(f"  Eigenvalues: {eigenvalues}")
        print(f"  Type: {kind}")
        results.append((point, eigenvalues, J, kind))
    return results


def stability_analysis():
    ml = MorrisLecar()
    ml_rhs = lambda state: ml.reduced_derivatives(state, 90.0)
    ml_guesses = [[V, 0.1] for V in [-40, -20, 0, 20]]
    ml_results = stability(ml_rhs, find_equilibria(ml_rhs, ml_guesses), "Morris-Lecar")

    hh = HodgkinHuxley()
    hh_rhs = lambda state: hh_reduced_derivatives(hh, state, 10.0)
    hh_guesses = [
        [V, n] for V in [-70, -60, -50, -40, -20, 0, 20] for n in [0.2, 0.5, 0.8]
    ]
    hh_results = stability(hh_rhs, find_equilibria(hh_rhs, hh_guesses), "Simplified HH")
    return ml_results, hh_results


def linearization_plot(results):
    ml = MorrisLecar()
    point, _, J, kind = next(result for result in results if result[3] == "Stable")
    time = np.linspace(0, 100, 5000)
    perturbation = np.array([2.0, 0.01])
    _, nonlinear = simulate(ml, point + perturbation, time, 90.0)
    linear = (
        solve_ivp(
            lambda t, x: J @ x,
            (0, 100),
            perturbation,
            t_eval=time,
            rtol=1e-6,
            atol=1e-8,
        ).y.T
        + point
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    plot_trace(axes[0], time, nonlinear[:, 0], label="Nonlinear")
    plot_trace(axes[0], time, linear[:, 0], label="Linearized", color="r", style="--")
    axes[0].legend()
    style_axes(axes[0], "Time (ms)", "Voltage V (mV)", "Voltage")
    axes[1].plot(nonlinear[:, 0], nonlinear[:, 1], "b", label="Nonlinear")
    axes[1].plot(linear[:, 0], linear[:, 1], "r--", label="Linearized")
    axes[1].scatter(*point, c="k", s=100, label=kind)
    axes[1].legend()
    style_axes(axes[1], "Voltage V (mV)", "Activation w", "Phase plane")
    save_figure(fig, "4_linearization.png")


def hh_linearization_plot(results):
    model = HodgkinHuxley()
    point, eigenvalues, J, kind = next(
        result for result in results if np.any(np.abs(result[1].imag) > 1e-8)
    )
    time = np.linspace(0, 3, 1000)
    perturbation = np.array([0.1, 0.001])
    nonlinear = solve_ivp(
        lambda t, x: hh_reduced_derivatives(model, x, 10.0),
        (0, 3),
        point + perturbation,
        t_eval=time,
        rtol=1e-6,
        atol=1e-8,
    ).y.T
    linear = (
        solve_ivp(
            lambda t, x: J @ x, (0, 3), perturbation, t_eval=time, rtol=1e-6, atol=1e-8
        ).y.T
        + point
    )
    print(f"Simplified HH linearization: {kind}, eigenvalues={eigenvalues}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    plot_trace(axes[0], time, nonlinear[:, 0], label="Nonlinear")
    plot_trace(axes[0], time, linear[:, 0], label="Linearized", color="r", style="--")
    axes[0].legend()
    style_axes(axes[0], "Time (ms)", "Voltage V (mV)", "Voltage")
    axes[1].plot(nonlinear[:, 0], nonlinear[:, 1], "b", label="Nonlinear")
    axes[1].plot(linear[:, 0], linear[:, 1], "r--", label="Linearized")
    axes[1].scatter(*point, c="k", s=100, label=kind)
    axes[1].legend()
    style_axes(axes[1], "Voltage V (mV)", "Activation n", "Phase plane")
    save_figure(fig, "5_hh_linearization.png")


def main():
    print("Phase portraits")
    phase_portrait_comparison()
    print("Nullclines")
    ml_nullclines()
    hh_nullclines()
    print("Equilibria and stability")
    ml_results, hh_results = stability_analysis()
    print("Linearization")
    linearization_plot(ml_results)
    hh_linearization_plot(hh_results)


if __name__ == "__main__":
    main()
