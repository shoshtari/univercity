import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from typing import Any, Callable, Union
import itertools


class SCM:
    def __init__(self) -> None:
        self.variables: dict[str, dict] = {}
        self.equations: dict[str, Callable] = {}
        self.parents: dict[str, list[str]] = {}
        self.topological_order: list[str] = []

    def add_variable(self, name: str, parents: list[str], equation: Callable) -> None:
        if name in self.variables:
            raise ValueError(f"{name} already exists")

        for parent in parents:
            if parent not in self.variables:
                raise ValueError(f"{parent} not found")

        self.variables[name] = {"parents": parents, "equation": equation}
        self.equations[name] = equation
        self.parents[name] = parents

        self._topol_sort()

    def _topol_sort(self) -> None:
        if not self.variables:
            self.topological_order = []
            return

        graph = {}
        children = {}
        queue = []
        for var in self.variables:
            graph[var] = set(self.parents[var])
            for parent in self.parents[var]:
                if parent not in children:
                    children[parent] = []
                children[parent].append(var)

            if len(graph[var]) == 0:
                queue.append(var)
        order = []

        while queue:
            var = queue.pop(0)
            order.append(var)

            for child in children.get(var, []):
                graph[child].remove(var)
                if len(graph[child]) == 0:
                    queue.append(child)

        assert len(order) == len(self.variables)
        self.topological_order = order

    def sample(self, n_samples: int) -> pd.DataFrame:
        if not self.variables:
            raise ValueError("No variables in the model.")

        samples = {}

        for var in self.topological_order:
            if var not in self.equations:
                continue

            parent_values = {}
            for parent in self.parents[var]:
                if parent not in samples:
                    raise ValueError(
                        f"Parent '{parent}' not sampled yet. Check topological order."
                    )
                parent_values[parent] = samples[parent]

            try:
                samples[var] = self.equations[var](parent_values, n_samples)
            except Exception as e:
                raise RuntimeError(f"Error sampling variable '{var}': {e}")

        return pd.DataFrame(samples)

    def do_operator(self, interventions: dict[str, Any]) -> "SCM":
        new_scm = SCM()

        for var, _ in self.variables.items():
            if var not in interventions:
                new_scm.add_variable(var, self.parents[var], self.equations[var])
                continue

            intervention_value = interventions[var]

            new_scm.add_variable(
                var, [], lambda _, n: np.full(n, intervention_value)
            )
        return new_scm

    def plot_graph(self, title: str = "Causal Graph") -> None:
        if not self.variables:
            print("No variables in the model.")
            return

        G = nx.DiGraph()

        for var in self.variables:
            G.add_node(var)

        for var, parents in self.parents.items():
            for parent in parents:
                G.add_edge(parent, var)


        plt.figure(figsize=(10, 8))
        nx.draw(
            G,
            with_labels=True,
            node_size=2000,
            arrowsize=20,
        )

