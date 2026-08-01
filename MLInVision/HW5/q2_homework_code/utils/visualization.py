import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils.functions import rosenbrock

def plot_rosenbrock_3d(
    x_range=(-2, 2),
    y_range=(-1, 3),
    resolution=300,
    paths=None,
    optimal_point=None,
):
    # Expand the surface domain to contain every path
    if paths:
        all_points = np.concatenate(
            [np.asarray(path, dtype=float) for path in paths.values()],
            axis=0,
        )

        padding = 0.1
        x_range = (
            min(x_range[0], all_points[:, 0].min() - padding),
            max(x_range[1], all_points[:, 0].max() + padding),
        )
        y_range = (
            min(y_range[0], all_points[:, 1].min() - padding),
            max(y_range[1], all_points[:, 1].max() + padding),
        )

    x = np.linspace(*x_range, resolution)
    y = np.linspace(*y_range, resolution)
    X, Y = np.meshgrid(x, y)
    Z = rosenbrock(X, Y)

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(
        X,
        Y,
        Z,
        cmap="viridis",
        edgecolor="none",
        alpha=1.0,            # Avoid transparent 3D depth-sorting artifacts
        antialiased=True,
    )

    if paths:
        colors = ["#FF4444", "#44FF44", "#4444FF"]

        for idx, (label, path) in enumerate(paths.items()):
            path = np.asarray(path, dtype=float)
            px = path[:, 0]
            py = path[:, 1]
            pz = rosenbrock(px, py)

            color = colors[idx % len(colors)]

            # A tiny offset prevents the line from disappearing into the surface.
            # Remove this offset if exact placement is more important.
            offset = max(np.ptp(Z), 1.0) * 1e-4
            ax.plot(
                px, py, pz + offset,
                color=color,
                linewidth=3,
                label=label,
            )
            ax.scatter(
                px, py, pz + offset,
                color=color,
                s=15,
                depthshade=False,
            )

    if optimal_point is not None:
        ox, oy = optimal_point
        oz = rosenbrock(ox, oy)

        ax.scatter(
            [ox], [oy], [oz],
            color="red",
            s=120,
            marker="*",
            label="Optimal",
        )

    ax.set_xlim(x_range)
    ax.set_ylim(y_range)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("f(x, y)")
    ax.set_title("Rosenbrock Function with Optimization Paths")

    if paths or optimal_point is not None:
        ax.legend()

    plt.tight_layout()

def plot_convergence(histories, metric="loss", title=None):
    plt.figure(figsize=(10, 6))
    for label, history in histories.items():
        values = history[metric]
        values = np.log(values)
        plt.plot(values, label=label)
    plt.xlabel("Round")
    plt.ylabel(metric.replace("_", " ").title())
    plt.title(title or f"{metric.replace('_', ' ').title()} vs Round")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
