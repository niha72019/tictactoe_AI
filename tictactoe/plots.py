"""Draws the comparison charts into results/plots/ from the CSVs in results/."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from . import config

SERIES = {"minimax": "#2a78d6", "alphabeta": "#eb6834"}
NAMES = {"minimax": "Minimax", "alphabeta": "Alpha-Beta"}
OUTCOME = {"win": "#0ca30c", "draw": "#898781", "loss": "#d03b3b"}
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e6e5e1", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 12, "font.size": 10,
    "legend.frameon": False,
})

def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(config.PLOTS_DIR, name), dpi=150)
    plt.close(fig)


def plot_depth_scaling(df):
    """Positions searched vs search depth from the empty board, one chart per board size."""
    sizes = sorted(df.board_size.unique())
    fig, axes = plt.subplots(1, len(sizes), figsize=(6.5 * len(sizes), 4.2), squeeze=False)
    for ax, n in zip(axes[0], sizes):
        sub = df[df.board_size == n]
        k = sub.win_length.iloc[0]
        for algo in ("minimax", "alphabeta"):
            d = sub[sub.algorithm == algo].sort_values("depth")
            ax.plot(d.depth, d.nodes, color=SERIES[algo], lw=2, marker="o", ms=5,
                    label=NAMES[algo])
            last = d.iloc[-1]
            ax.annotate(f"{NAMES[algo]}  {last.nodes:,.0f}", (last.depth, last.nodes),
                        xytext=(6, 0), textcoords="offset points", va="center",
                        fontsize=8.5, color=INK2)
        ax.set_yscale("log")
        ax.set_xticks(sorted(sub.depth.unique()))
        ax.set_xlim(right=sub.depth.max() + 1.2)
        ax.set_title(f"Positions searched vs depth\n{n}x{n} board, {k} in a row, from the empty board",
                     loc="left")
        ax.set_xlabel("Search depth (plies)")
        ax.set_ylabel("Positions searched (log scale)")
        ax.legend(loc="upper left")
    save(fig, "depth_scaling_nodes.png")


def grouped_bars(summary, metric, xlabel, title, fname, log=True):
    configs = list(dict.fromkeys(summary.config))
    fig, ax = plt.subplots(figsize=(8, 0.75 * len(configs) + 1.4))
    h = 0.36
    for j, algo in enumerate(("minimax", "alphabeta")):
        sub = summary[summary.algorithm == algo].set_index("config").reindex(configs)
        ys = [i + (j - 0.5) * (h + 0.04) for i in range(len(configs))]
        ax.barh(ys, sub[metric], height=h, color=SERIES[algo], label=NAMES[algo])
        for y, v in zip(ys, sub[metric]):
            ax.annotate(f"{v:,.0f}" if metric.endswith("nodes") else f"{v * 1000:,.2f} ms",
                        (v, y), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(configs)), configs)
    ax.invert_yaxis()
    if log:
        ax.set_xscale("log")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left")
    ax.legend(loc="lower right")
    ax.margins(x=0.15)
    save(fig, fname)


def node_saving_pct(summary):
    """% fewer positions Alpha-Beta searched than Minimax, per configuration."""
    return summary.drop_duplicates("config").set_index("config")["node_reduction_pct"]


def plot_reduction(summary):
    s = node_saving_pct(summary)
    fig, ax = plt.subplots(figsize=(8, 0.6 * len(s) + 1.4))
    ax.barh(s.index, s.values, color=SERIES["alphabeta"], height=0.55)
    for y, v in enumerate(s.values):
        ax.annotate(f"{v:.0f}%", (v, y), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK2)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("% fewer positions searched by Alpha-Beta than Minimax (same states)")
    ax.set_title("Alpha-Beta node reduction per configuration", loc="left")
    save(fig, "alphabeta_node_reduction.png")


def plot_outcomes(games):
    t = (games.groupby(["config", "algorithm", "outcome"], sort=False).size()
         .unstack(fill_value=0).reindex(columns=["win", "draw", "loss"], fill_value=0))
    t = t.div(t.sum(axis=1), axis=0) * 100
    labels = [f"{c}  ·  {NAMES[a]}" for c, a in t.index]
    fig, ax = plt.subplots(figsize=(8.5, 0.42 * len(t) + 1.6))
    left = pd.Series(0.0, index=t.index)
    for outcome in ("win", "draw", "loss"):
        vals = t[outcome]
        ax.barh(labels, vals, left=left, color=OUTCOME[outcome], height=0.62,
                edgecolor=SURFACE, linewidth=2, label=outcome.capitalize())
        for y, (v, l) in enumerate(zip(vals, left)):
            if v >= 8:
                ax.text(l + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=8,
                        color="#ffffff")
        left += vals
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.grid(False)
    ax.set_xlabel("% of games vs random baseline (AI as X and as O combined)")
    ax.set_title("Outcomes against a random opponent", loc="left", pad=24)
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), borderaxespad=0.2)
    save(fig, "outcomes_vs_random.png")


def main():
    r = config.RESULTS_DIR
    os.makedirs(config.PLOTS_DIR, exist_ok=True)
    summary = pd.read_csv(os.path.join(r, "summary.csv"))
    plot_depth_scaling(pd.read_csv(os.path.join(r, "depth_scaling.csv")))
    grouped_bars(summary, "mean_nodes", "Mean nodes per search (log scale)",
                 "Nodes explored on identical states: Minimax vs Alpha-Beta",
                 "nodes_per_config.png")
    grouped_bars(summary, "mean_time_s", "Mean time per search (log scale)",
                 "Search time on identical states: Minimax vs Alpha-Beta",
                 "time_per_config.png")
    plot_reduction(summary)
    plot_outcomes(pd.read_csv(os.path.join(r, "games_vs_random.csv")))


if __name__ == "__main__":
    main()
