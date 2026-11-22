"""Scores an unfinished position when a depth-limited search stops before the game ends."""
from .config import HEURISTIC_SCALE
from .game import other


def open_line_counts(game, state, player):
    """{m: number of lines with exactly m of `player`'s marks and none of the opponent's}."""
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


def line_score(game, state, player):
    # A line the opponent hasn't blocked, holding m of my marks, is worth 10^(m-1):
    # 1 mark = 1, 2 marks = 10, 3 marks = 100, ...
    return sum(n * 10 ** (m - 1)
               for m, n in open_line_counts(game, state, player).items())


def evaluate(game, state, player):
    mine = line_score(game, state, player)
    theirs = line_score(game, state, other(player))
    # (mine - theirs) / (mine + theirs + 1) is always between -1 and 1; scaling it by
    # HEURISTIC_SCALE (0.5) keeps every estimate below a real win (+1) or loss (-1).
    return HEURISTIC_SCALE * (mine - theirs) / (mine + theirs + 1)
