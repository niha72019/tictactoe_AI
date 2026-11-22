"""Console output for the menu: the experiment summary table and the test run."""
import os

import pandas as pd
import pytest

from . import config
from .plots import node_saving_pct

LABEL_W = 30
COL_W = 12
GROUP_W = 2 * COL_W + 2   # one setting = Minimax column + Alpha-Beta column


def setting_name(cfg):
    """'3x3 k3 full' -> '3x3, full search';  '4x4 k4 d3' -> '4x4, 4 in a row, depth 3'."""
    board, k, depth = cfg.split()
    name = board
    if board != "3x3" or k != "k3":
        name += f", {k[1:]} in a row"
    if depth == "full":
        name += ", full search"
    else:
        name += f", depth {depth[1:]}"
    return name


def ms(seconds):
    return f"{seconds * 1000:,.1f} ms"


def print_experiment_summary():
    s = pd.read_csv(os.path.join(config.RESULTS_DIR, "summary.csv"))
    configs = list(dict.fromkeys(s.config))
    by = s.set_index(["config", "algorithm"])

    def row(label, cells):
        """cells: one (Minimax text, Alpha-Beta text) pair per setting"""
        line = f"{label:<{LABEL_W}}"
        for mm, ab in cells:
            line += f"    {mm:>{COL_W}}  {ab:>{COL_W}}"
        print(line)

    print()
    line = f"{'':<{LABEL_W}}"
    for c in configs:
        line += f"    {setting_name(c):^{GROUP_W}}"
    print(line)
    row("", [("Minimax", "Alpha-Beta") for c in configs])
    print("-" * (LABEL_W + len(configs) * (GROUP_W + 4)))

    nodes, times, results = [], [], []
    for c in configs:
        mm, ab = by.loc[(c, "minimax")], by.loc[(c, "alphabeta")]
        nodes.append((f"{mm.mean_nodes:,.0f}", f"{ab.mean_nodes:,.0f}"))
        times.append((ms(mm.mean_time_s), ms(ab.mean_time_s)))
        results.append(tuple(f"{r.vs_random_win:.0f}/{r.vs_random_draw:.0f}/{r.vs_random_loss:.0f}"
                             for r in (mm, ab)))
    row("Positions searched per move", nodes)
    row("Time per move", times)
    row("vs random player (W/D/L)", results)

    line = f"{'Same move chosen':<{LABEL_W}}"
    for c in configs:
        r = by.loc[(c, "minimax")]
        same = round(r.same_move_rate * r.states)
        line += f"    {f'{same} of {r.states:.0f} positions':^{GROUP_W}}"
    print(line)

    saving = node_saving_pct(s)
    parts = [f"{saving[c]:.0f}% fewer on {c.split()[0]}" for c in configs]
    print(f"\nAlpha-Beta searched {' and '.join(parts)}.".replace(" fewer on", " fewer positions on", 1))
    print("Depth comparison chart saved.")
    print(f"Charts saved to: {config.PLOTS_DIR}")


def run_tests():
    """Run every test in tests/; True if all passed."""
    return pytest.main(["-v", os.path.join(config.PROJECT_DIR, "tests")]) == 0
