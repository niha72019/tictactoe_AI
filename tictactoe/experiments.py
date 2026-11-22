"""
experiments.py - runs every experiment and writes the measured results to CSV.

Nothing here is typed in by hand: every number in results/*.csv comes from
actually running the search code.

    python -m tictactoe.experiments            # settings are in config.py

Outputs (in results/):
  state_comparison.csv  Minimax vs Alpha-Beta on identical, seeded random states
                        (one row per state per algorithm: move, value, nodes, time)
  games_vs_random.csv   one row per game: AI (minimax / alphabeta) vs random baseline
  ai_vs_ai.csv          Minimax vs Alpha-Beta games, both colour assignments
  depth_scaling.csv     nodes and time from the empty board vs search depth
  summary.csv           aggregated table built from the files above
"""
import os
import random

import pandas as pd

from . import config
from .agents import RandomAgent, SearchAgent, outcome_for, play_game
from .config import GameSettings
from .game import TicTacToe, X, O
from .search import ALGORITHMS


def label(s):
    depth = "full" if s.max_depth is None else f"d{s.max_depth}"
    return f"{s.board_size}x{s.board_size} k{s.win_length} {depth}"


def timed_search(algorithm, game, state, depth, repeats):
    """Run a search `repeats` times; keep its result and the median time
    (the middle one of the sorted times)."""
    fn = ALGORITHMS[algorithm]
    results = [fn(game, state, depth) for _ in range(repeats)]
    r = results[0]
    times = [x.time_s for x in results]
    r.time_s = sorted(times)[len(times) // 2]
    return r


# --------------------------------------------------------------------------
# 1. Minimax vs Alpha-Beta on identical board states
# --------------------------------------------------------------------------
def random_states(game, count, rng):
    """Distinct non-terminal states reached by random play of random length."""
    states, seen, attempts = [], set(), 0
    max_plies = game.n * game.n - 1
    while len(states) < count and attempts < count * 50:
        attempts += 1
        state = game.initial_state()
        for _ in range(rng.randint(0, max_plies)):
            if game.is_terminal(state):
                break
            state = game.result(state, rng.choice(game.actions(state)))
        if not game.is_terminal(state) and state not in seen:
            seen.add(state)
            states.append(state)
    return states


def run_state_comparison(configs, states_per_config, repeats, seed):
    rows = []
    for s in configs:
        game = TicTacToe(s)
        # seeded by the setting's name (not its place in the list), so adding or
        # reordering settings never changes the positions another setting is tested on
        states = random_states(game, states_per_config, random.Random(f"{seed}:{label(s)}"))
        for si, state in enumerate(states):
            for algo in ("minimax", "alphabeta"):
                r = timed_search(algo, game, state, s.max_depth, repeats)
                rows.append(dict(config=label(s), board_size=s.board_size,
                                 win_length=s.win_length,
                                 max_depth=s.max_depth if s.max_depth else "full",
                                 state_id=si, state="".join(state),
                                 empty_cells=len(game.actions(state)),
                                 algorithm=algo, move=r.move, value=round(r.value, 6),
                                 nodes=r.nodes, time_s=r.time_s, cutoffs=r.cutoffs))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# 2. Games against the random baseline, and AI vs AI
# --------------------------------------------------------------------------
def play_logged(game, agent_x, agent_o, ai_agents):
    for a in ai_agents:
        a.history.clear()
    record = play_game(game, agent_x, agent_o)
    stats = {}
    for a in ai_agents:
        side = X if a is agent_x else O
        stats[side] = dict(moves=len(a.history),
                           nodes=sum(h.nodes for h in a.history),
                           time_s=sum(h.time_s for h in a.history))
    return record, stats


def run_games_vs_random(configs, games, seed):
    rows = []
    for s in configs:
        game = TicTacToe(s)
        for algo in ("minimax", "alphabeta"):
            for ai_side in (X, O):
                for g in range(games):
                    ai = SearchAgent(algo, s.max_depth)
                    rnd = RandomAgent(seed + g)    # same opponent seeds for both algorithms
                    agent_x, agent_o = (ai, rnd) if ai_side == X else (rnd, ai)
                    record, stats = play_logged(game, agent_x, agent_o, [ai])
                    st = stats[ai_side]
                    rows.append(dict(config=label(s), board_size=s.board_size,
                                     win_length=s.win_length,
                                     max_depth=s.max_depth if s.max_depth else "full",
                                     algorithm=algo, ai_side=ai_side, game=g,
                                     random_seed=seed + g,
                                     outcome=outcome_for(record, ai_side),
                                     total_moves=len(record.moves), ai_moves=st["moves"],
                                     ai_nodes=st["nodes"], ai_time_s=st["time_s"],
                                     moves=" ".join(map(str, record.moves))))
    return pd.DataFrame(rows)


def run_ai_vs_ai(configs):
    rows = []
    for s in configs:
        game = TicTacToe(s)
        for algo_x, algo_o in (("minimax", "alphabeta"), ("alphabeta", "minimax"),
                               ("minimax", "minimax"), ("alphabeta", "alphabeta")):
            ax, ao = SearchAgent(algo_x, s.max_depth), SearchAgent(algo_o, s.max_depth)
            record, stats = play_logged(game, ax, ao, [ax, ao])
            rows.append(dict(config=label(s), x_algorithm=algo_x, o_algorithm=algo_o,
                             winner=record.winner or "draw", total_moves=len(record.moves),
                             x_nodes=stats[X]["nodes"], o_nodes=stats[O]["nodes"],
                             x_time_s=stats[X]["time_s"], o_time_s=stats[O]["time_s"],
                             moves=" ".join(map(str, record.moves))))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# 3. Depth scaling from the empty board
# --------------------------------------------------------------------------
def run_depth_scaling(scaling, repeats):
    rows = []
    for n, spec in scaling.items():
        for d in spec["depths"]:
            s = GameSettings(n, spec["win_length"], d)
            game = TicTacToe(s)
            for algo in ("minimax", "alphabeta"):
                r = timed_search(algo, game, game.initial_state(), d, repeats)
                rows.append(dict(board_size=n, win_length=s.win_length, depth=d,
                                 algorithm=algo, move=r.move, value=round(r.value, 6),
                                 nodes=r.nodes, time_s=r.time_s, cutoffs=r.cutoffs))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
def build_summary(states, games):
    """One row per setting and algorithm, built from the two detailed tables."""
    rows = []
    configs = []                                  # settings, in the order they were run
    for c in states["config"]:
        if c not in configs:
            configs.append(c)

    for c in configs:
        st = states[states["config"] == c]
        mm = st[st["algorithm"] == "minimax"]
        ab = st[st["algorithm"] == "alphabeta"]

        # did both algorithms pick the same move / value on each position?
        same_move = 0
        same_value = 0
        mm_moves, ab_moves = list(mm["move"]), list(ab["move"])
        mm_values, ab_values = list(mm["value"]), list(ab["value"])
        for i in range(len(mm_moves)):
            if mm_moves[i] == ab_moves[i]:
                same_move += 1
            if mm_values[i] == ab_values[i]:
                same_value += 1
        n = len(mm_moves)

        # % fewer positions searched = 1 - (Alpha-Beta average / Minimax average)
        reduction = 100 * (1 - ab["nodes"].mean() / mm["nodes"].mean())

        for algo, part in (("minimax", mm), ("alphabeta", ab)):
            g = games[(games["config"] == c) & (games["algorithm"] == algo)]
            rows.append({
                "config": c,
                "algorithm": algo,
                "states": len(part),
                "mean_nodes": part["nodes"].mean(),
                "total_nodes": part["nodes"].sum(),
                "mean_time_s": part["time_s"].mean(),
                "total_time_s": part["time_s"].sum(),
                "same_move_rate": same_move / n,
                "same_value_rate": same_value / n,
                "node_reduction_pct": reduction,
                "vs_random_win": (g["outcome"] == "win").sum(),
                "vs_random_draw": (g["outcome"] == "draw").sum(),
                "vs_random_loss": (g["outcome"] == "loss").sum(),
            })
    return pd.DataFrame(rows)


def main():
    configs = config.EXPERIMENT_CONFIGS
    repeats = config.TIMING_REPEATS
    seed = config.RANDOM_SEED
    out = config.RESULTS_DIR
    os.makedirs(out, exist_ok=True)

    # 1. Minimax vs Alpha-Beta on identical states
    states = run_state_comparison(configs, config.STATES_PER_CONFIG, repeats, seed)
    states.to_csv(os.path.join(out, "state_comparison.csv"), index=False)

    # 2. Games vs random baseline
    games = run_games_vs_random(configs, config.GAMES_VS_RANDOM, seed)
    games.to_csv(os.path.join(out, "games_vs_random.csv"), index=False)

    # 3. AI vs AI
    run_ai_vs_ai(configs).to_csv(os.path.join(out, "ai_vs_ai.csv"), index=False)

    # 4. Depth scaling
    run_depth_scaling(config.DEPTH_SCALING, repeats).to_csv(
        os.path.join(out, "depth_scaling.csv"), index=False)

    summary = build_summary(states, games)
    summary.to_csv(os.path.join(out, "summary.csv"), index=False)


if __name__ == "__main__":
    main()
