"""
config.py - every tunable setting of the project lives here, and only here.

Other modules never hard-code a board size, win length or search depth;
they read these values (or receive a `GameSettings` built from them).
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GameSettings:
    """One game configuration: board size, win length and search depth.

    board_size : N for an N x N board.
    win_length : how many marks in a line are needed to win (K <= N).
    max_depth  : how many plies the AI looks ahead; None = search to the end
                 of the game (exact Minimax, only practical for 3x3).
    """
    board_size: int = 3
    win_length: int = 3
    max_depth: Optional[int] = None

    def __post_init__(self):
        if self.board_size < 1:
            raise ValueError("board_size must be >= 1")
        if not 1 <= self.win_length <= self.board_size:
            raise ValueError("win_length must be between 1 and board_size")
        if self.max_depth is not None and self.max_depth < 1:
            raise ValueError("max_depth must be >= 1 or None")


# --------------------------------------------------------------------------
# Default game (used by the console game, the GUI and the tests)
# --------------------------------------------------------------------------
BOARD_SIZE = 3
WIN_LENGTH = 3
SEARCH_DEPTH: Optional[int] = None          # None = full (exact) search

DEFAULT_SETTINGS = GameSettings(BOARD_SIZE, WIN_LENGTH, SEARCH_DEPTH)

# Default search depth offered for boards larger than 3x3 in the
# interactive game, where a full search is infeasible.
LARGE_BOARD_DEFAULT_DEPTH = 3

# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
# Terminal utilities, from the point of view of the player the AI plays for
# (the "Max" player): +1 win, -1 loss, 0 draw (as in the synopsis).
WIN_SCORE = 1.0
DRAW_SCORE = 0.0
# Small penalty per ply so the AI prefers a quicker win and a slower loss.
# It never changes a win into a non-win: 1 - 0.01 * plies stays > 0.5.
DEPTH_PENALTY = 0.01
# Heuristic estimates of non-terminal positions are scaled into
# (-HEURISTIC_SCALE, +HEURISTIC_SCALE), safely below any real win/loss.
HEURISTIC_SCALE = 0.5

# --------------------------------------------------------------------------
# Experiments
# --------------------------------------------------------------------------
RANDOM_SEED = 42
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
PLOTS_DIR = RESULTS_DIR / "plots"

# Configurations used for the Minimax vs Alpha-Beta comparison on
# identical board states and for the games against the random baseline.
EXPERIMENT_CONFIGS = [
    GameSettings(board_size=3, win_length=3, max_depth=None),   # exact
    GameSettings(board_size=4, win_length=4, max_depth=3),
]

# Number of random (but reproducible) board states per configuration
# on which Minimax and Alpha-Beta are compared move-for-move.
STATES_PER_CONFIG = 40

# Games played by each agent against the random baseline,
# per configuration and per side (as X and as O).
GAMES_VS_RANDOM = 20

# Depth-scaling experiment: depths searched from the empty board.
DEPTH_SCALING = {
    4: dict(win_length=4, depths=[1, 2, 3, 4]),
}

# Each search in the experiments is timed this many times; the median is kept.
TIMING_REPEATS = 3
