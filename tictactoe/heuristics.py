"""
heuristics.py - evaluation of non-terminal states for depth-limited search.

When the search is cut off before the game ends (needed for N x N boards),
the position is scored by counting "open lines": lines of length K that
contain marks of only one player, so that player could still complete them.

A line with m of my marks and no opponent marks is worth 10**(m-1):
one mark = 1, two marks = 10, a near-win (K-1 marks) much more.
The score is (mine - theirs) / (mine + theirs + 1), which lies strictly in
(-1, 1), then multiplied by HEURISTIC_SCALE so a heuristic estimate is
always smaller than a real win (+1) or loss (-1).
"""
from .config import HEURISTIC_SCALE
from .game import EMPTY, State, TicTacToe, other


def open_line_counts(game: TicTacToe, state: State, player: str) -> dict:
    """{m: number of open lines holding exactly m of `player`'s marks}."""
    opponent = other(player)
    counts = {}
    for line in game.lines:
        mine = 0
        blocked = False
        for i in line:
            cell = state[i]
            if cell == player:
                mine += 1
            elif cell == opponent:
                blocked = True
                break
        if not blocked and mine > 0:
            counts[mine] = counts.get(mine, 0) + 1
    return counts


def line_score(game: TicTacToe, state: State, player: str) -> float:
    return sum(n * 10 ** (m - 1)
               for m, n in open_line_counts(game, state, player).items())


def evaluate(game: TicTacToe, state: State, player: str) -> float:
    """Heuristic value of `state` for `player`, in (-HEURISTIC_SCALE, HEURISTIC_SCALE)."""
    mine = line_score(game, state, player)
    theirs = line_score(game, state, other(player))
    return HEURISTIC_SCALE * (mine - theirs) / (mine + theirs + 1)
