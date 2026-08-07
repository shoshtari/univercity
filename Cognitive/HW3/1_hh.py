import numpy as np
import matplotlib.pyplot as plt

from common import HodgkinHuxley, plot_trace, save_figure, simulate_hh, style_axes

INITIAL_STATE = [-65.0, 0.317, 0.05, 0.6]


def pulse(amplitude, duration):
    return lambda time: amplitude if time < duration else 0.0


def count_spikes(voltage, time, threshold=0.0):
    crossings = (voltage[:-1] < threshold) & (voltage[1:] >= threshold)
    crossings = np.r_[False, crossings]
    return crossings.sum(), time[crossings]


def save(fig, number, name):
    save_figure(fig, f"{number}_{name}.png")


def plot_voltage(ax, solution, title, threshold=False):
    plot_trace(ax, solution.t, solution.y[0])
    if threshold:
        ax.axhline(0, color="r", linestyle="--", alpha=0.3)
    style_axes(ax, "Time (ms)", "V (mV)", title)


def plot_pulse_grid(model, cases, figure_title, filename, time_end):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(figure_title)
    for ax, (label, amplitude, duration) in zip(axes.flat, cases):
        solution = simulate_hh(
            model, pulse(amplitude, duration), (0, time_end), INITIAL_STATE
        )
        plot_voltage(ax, solution, label, threshold=True)
    save(fig, *filename)


def find_threshold(model):
    def spikes(amplitude):
        solution = simulate_hh(model, pulse(amplitude, 1.0), (0, 50), INITIAL_STATE)
        return solution.y[0].max() > 0

    low, high = 0.0, 50.0
    for _ in range(30):
        middle = (low + high) / 2
        if spikes(middle):
            high = middle
        else:
            low = middle
    return (low + high) / 2


def threshold_plots(model):
    threshold = find_threshold(model)
    print(f"Threshold current (1 ms pulse): {threshold:.3f} uA/cm^2")

    currents = np.linspace(0, 20, 200)
    maxima = []
    for current in currents:
        solution = simulate_hh(model, pulse(current, 1.0), (0, 50), INITIAL_STATE)
        maxima.append(solution.y[0].max())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(currents, maxima, "b-", lw=2)
    ax.axvline(
        threshold, color="g", linestyle="--", label=f"Threshold = {threshold:.2f}"
    )
    ax.axhline(0, color="r", linestyle="--", alpha=0.5, label="Spike level")
    ax.legend()
    style_axes(ax, "Applied current (uA/cm^2)", "Maximum V (mV)", "Threshold")
    save(fig, 1, "threshold_staircase")

    cases = [
        (f"I = {current:.2f}", current, 1.0)
        for current in [threshold - 1, threshold, threshold + 1, threshold + 5]
    ]
    plot_pulse_grid(model, cases, "Threshold responses", (2, "threshold_traces"), 30)
    return threshold


def current_plots(model):
    amplitude_cases = [(f"I = {current}", current, 1.0) for current in [5, 10, 20, 30]]
    plot_pulse_grid(
        model, amplitude_cases, "Current amplitude", (3, "amplitude_effect"), 30
    )

    duration_cases = [
        (f"Duration = {duration} ms", 10, duration)
        for duration in [0.5, 1.0, 3.0, 10.0]
    ]
    plot_pulse_grid(model, duration_cases, "Pulse duration", (4, "duration_effect"), 40)

    currents = np.linspace(0, 30, 30)
    rates = []
    for current in currents:
        solution = simulate_hh(model, lambda time: current, (0, 200), INITIAL_STATE)
        _, spike_times = count_spikes(solution.y[0], solution.t)
        spike_times = spike_times[spike_times > 20]
        rates.append(
            1000 / np.mean(np.diff(spike_times)) if len(spike_times) > 1 else 0
        )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(currents, rates, "b-o", ms=3)
    style_axes(ax, "Current amplitude (uA/cm^2)", "Frequency (Hz)", "f-I curve")
    save(fig, 5, "fi_curve")


def initial_condition_plot(model):
    conditions = [
        ("Default", [-65, 0.317, 0.05, 0.6]),
        ("Depolarized", [-60, 0.35, 0.08, 0.5]),
        ("Hyperpolarized", [-70, 0.28, 0.02, 0.7]),
        ("High n", [-65, 0.50, 0.05, 0.6]),
        ("High m", [-65, 0.317, 0.15, 0.6]),
        ("Low h", [-65, 0.317, 0.05, 0.3]),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Initial conditions")
    for ax, (label, state) in zip(axes.flat, conditions):
        solution = simulate_hh(model, pulse(10, 1.0), (0, 30), state)
        plot_voltage(ax, solution, label, threshold=True)
    save(fig, 6, "initial_conditions")


def conductance_plots(model):
    for number, parameter, values, name in [
        (7, "g_Na", [60, 120, 180, 240], "gNa_effect"),
        (8, "g_K", [18, 36, 54, 72], "gK_effect"),
    ]:
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(parameter)
        for ax, value in zip(axes.flat, values):
            varied_model = HodgkinHuxley(**{parameter: value})
            solution = simulate_hh(varied_model, pulse(10, 1.0), (0, 30), INITIAL_STATE)
            plot_voltage(ax, solution, f"{parameter} = {value}")
        save(fig, number, name)

    sodium_values = np.linspace(60, 200, 15)
    potassium_values = np.linspace(18, 72, 15)
    frequency_map = np.zeros((len(potassium_values), len(sodium_values)))
    for row, potassium in enumerate(potassium_values):
        for column, sodium in enumerate(sodium_values):
            varied_model = HodgkinHuxley(g_Na=sodium, g_K=potassium)
            solution = simulate_hh(
                varied_model, lambda time: 10.0, (0, 150), INITIAL_STATE
            )
            _, spike_times = count_spikes(solution.y[0], solution.t)
            spike_times = spike_times[spike_times > 20]
            if len(spike_times) > 1:
                frequency_map[row, column] = 1000 / np.mean(np.diff(spike_times))

    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(
        frequency_map,
        origin="lower",
        aspect="auto",
        cmap="viridis",
        extent=[
            sodium_values[0],
            sodium_values[-1],
            potassium_values[0],
            potassium_values[-1],
        ],
    )
    fig.colorbar(image, label="Frequency (Hz)")
    style_axes(ax, "g_Na (mS/cm^2)", "g_K (mS/cm^2)", "Frequency map")
    save(fig, 9, "gNa_gK_map")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for leak in [0.1, 0.3, 1.0, 3.0]:
        varied_model = HodgkinHuxley(g_L=leak)
        resting = simulate_hh(varied_model, lambda time: 0.0, (0, 50), INITIAL_STATE)
        stimulated = simulate_hh(varied_model, pulse(10, 1.0), (0, 30), INITIAL_STATE)
        axes[0].plot(resting.t, resting.y[0], label=f"g_L = {leak}")
        axes[1].plot(stimulated.t, stimulated.y[0], label=f"g_L = {leak}")
    for ax, title in zip(axes, ["Resting response", "Pulse response"]):
        ax.legend()
        style_axes(ax, "Time (ms)", "V (mV)", title)
    save(fig, 10, "gL_effect")


def sensitivity_plot(model):
    parameters = {"g_Na": 120.0, "g_K": 36.0, "g_L": 0.3, "C": 1.0}
    scales = np.linspace(0.5, 1.5, 11)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for parameter, value in parameters.items():
        peaks, widths, counts = [], [], []
        for scale in scales:
            varied = dict(parameters)
            varied[parameter] = value * scale
            solution = simulate_hh(
                HodgkinHuxley(**varied), pulse(10, 1.0), (0, 30), INITIAL_STATE
            )
            voltage = solution.y[0]
            peak = voltage.max()
            half_height = voltage.min() + (peak - voltage.min()) / 2
            above_half = solution.t[voltage > half_height]
            peaks.append(peak)
            widths.append(above_half[-1] - above_half[0] if len(above_half) > 1 else 0)
            counts.append(count_spikes(voltage, solution.t)[0])
        axes[0].plot(scales, peaks, "-o", ms=3, label=parameter)
        axes[1].plot(scales, widths, "-o", ms=3, label=parameter)
        axes[2].plot(scales, counts, "-o", ms=3, label=parameter)

    for ax, ylabel, title in zip(
        axes,
        ["Peak V (mV)", "AP width (ms)", "Spike count"],
        ["Peak", "Width", "Spike count"],
    ):
        ax.legend()
        style_axes(ax, "Parameter scale", ylabel, title)
    save(fig, 11, "sensitivity")


def subthreshold_plots(model, threshold):
    cases = [(f"I = {current}", current, 50) for current in [0.5, 1.0, 1.5, 2.0]]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Subthreshold responses")
    for ax, (label, current, duration) in zip(axes.flat, cases):
        solution = simulate_hh(
            model, lambda time: current, (0, duration), INITIAL_STATE
        )
        plot_voltage(ax, solution, label)
    save(fig, 12, "subthreshold_traces")

    currents = np.linspace(0, threshold * 0.95, 25)
    depolarization = []
    for current in currents:
        solution = simulate_hh(model, lambda time: current, (0, 30), INITIAL_STATE)
        depolarization.append(solution.y[0, -1] + 65.0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(currents, depolarization, "b-o", ms=3)
    style_axes(
        ax, "Input current (uA/cm^2)", "Depolarization (mV)", "Subthreshold response"
    )
    save(fig, 13, "subthreshold_depol")

    solution = simulate_hh(model, pulse(1.5, 100), (0, 30), INITIAL_STATE)
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    plot_trace(axes[0], solution.t, solution.y[0], color="k")
    style_axes(axes[0], "", "V (mV)", "Gating variables")
    for values, label in zip(solution.y[1:], ["n", "m", "h"]):
        axes[1].plot(solution.t, values, label=label)
    axes[1].legend()
    style_axes(axes[1], "Time (ms)", "Gating value")
    save(fig, 14, "subthreshold_gating")


model = HodgkinHuxley()
threshold = threshold_plots(model)
current_plots(model)
initial_condition_plot(model)
conductance_plots(model)
sensitivity_plot(model)
subthreshold_plots(model, threshold)
print("All figures saved to report/pics/")
