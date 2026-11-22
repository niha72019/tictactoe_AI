"""All tunable settings for the project."""
import os


class GameSettings:
    """Board size N, win length K, and how many moves ahead the AI looks (None = to the end)."""

    def __init__(self, board_size=3, win_length=3, max_depth=None):
        if board_size < 1:
            raise ValueError("board_size must be >= 1")
        if not 1 <= win_length <= board_size:
            raise ValueError("win_length must be between 1 and board_size")
        if max_depth is not None and max_depth < 1:
            raise ValueError("max_depth must be >= 1 or None")
        self.board_size = board_size
        self.win_length = win_length
        self.max_depth = max_depth


BOARD_SIZE = 3
WIN_LENGTH = 3
SEARCH_DEPTH = None                         # None = search to the end of the game

DEFAULT_SETTINGS = GameSettings(BOARD_SIZE, WIN_LENGTH, SEARCH_DEPTH)

LARGE_BOARD_DEFAULT_DEPTH = 3               # used beyond 3x3, where a full search is too slow

PLAY_HUMAN_SIDE = "X"                       # "X" (you move first) or "O"
PLAY_ALGORITHM = "alphabeta"                # "alphabeta" or "minimax"

WIN_SCORE = 1.0
DRAW_SCORE = 0.0
# Subtracted from a win once per move, so the AI prefers quicker wins and slower
# losses. Small enough that a win still always scores above 0.5.
DEPTH_PENALTY = 0.01
# Heuristic estimates stay within +/-0.5, below any real win or loss.
HEURISTIC_SCALE = 0.5

RANDOM_SEED = 42
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")

EXPERIMENT_CONFIGS = [
    GameSettings(board_size=3, win_length=3, max_depth=None),
    GameSettings(board_size=4, win_length=4, max_depth=3),
]

STATES_PER_CONFIG = 40
GAMES_VS_RANDOM = 20                        # per configuration, per side (X and O)

DEPTH_SCALING = {
    4: dict(win_length=4, depths=[1, 2, 3, 4]),
}

TIMING_REPEATS = 3                          # the median time is kept
