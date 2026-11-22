"""
search.py - adversarial search: plain Minimax and Minimax with Alpha-Beta pruning.

Both algorithms
  * treat the player to move at the root as Max and the opponent as Min,
  * score terminal states +1 (Max wins) / -1 (Min wins) / 0 (draw), minus a
    tiny per-ply penalty so faster wins are preferred,
  * optionally stop at `max_depth` plies and use the heuristic evaluation,
  * examine moves in the same (row-major) order and break ties the same way
    (first strictly-better move wins),
  * count every node (state) they visit and time themselves.

Because of the identical move order and tie-breaking, Alpha-Beta is
guaranteed to return the same move and value as Minimax - pruning only
skips branches that cannot change the decision. The tests check this.

Arguments used by the recursive functions:
  player     whose turn it is in `state`
  max_player the player the search is choosing a move for (the root player)
  last_move  the cell just played to reach `state` (to check for a win fast)
  depth      how many plies below the root `state` is
  max_depth  stop and use the heuristic at this depth (None = search to the end)
  counter    {"nodes": ..., "cutoffs": ...}, updated as the search runs
"""
import math
import time

from .config import DEPTH_PENALTY, DRAW_SCORE, WIN_SCORE
from .game import EMPTY, other
from .heuristics import evaluate


class SearchResult:
    """What one search returns."""

    def __init__(self, algorithm, move, value, nodes, time_s, max_depth, cutoffs=0):
        self.algorithm = algorithm
        self.move = move              # chosen cell index
        self.value = value            # backed-up value of the root for the player to move
        self.nodes = nodes            # number of states visited (root included)
        self.time_s = time_s          # wall-clock search time in seconds
        self.max_depth = max_depth
        self.cutoffs = cutoffs        # number of prunings (Alpha-Beta only)


def leaf_value(game, state, max_player, last_move, depth, max_depth):
    """Value if the search must stop here (game over or depth limit), else None."""
    if game.is_win_at(state, last_move):
        score = WIN_SCORE - DEPTH_PENALTY * depth
        if state[last_move] == max_player:
            return score
        return -score
    if EMPTY not in state:
        return DRAW_SCORE
    if max_depth is not None and depth >= max_depth:
        return evaluate(game, state, max_player)
    return None


def check_root(game, state):
    if game.is_terminal(state):
        raise ValueError("cannot search from a terminal state")


# ------------------------------------------------------------------ Minimax
def minimax(game, state, player, max_player, last_move, depth, max_depth, counter):
    counter["nodes"] += 1
    leaf = leaf_value(game, state, max_player, last_move, depth, max_depth)
    if leaf is not None:
        return leaf

    if player == max_player:                      # Max: take the highest value
        best = -math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = minimax(game, child, other(player), max_player, a, depth + 1, max_depth, counter)
            best = max(best, v)
    else:                                         # Min: take the lowest value
        best = math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = minimax(game, child, other(player), max_player, a, depth + 1, max_depth, counter)
            best = min(best, v)
    return best


def minimax_search(game, state, max_depth=None):
    """Best move for the player to move, by plain (exhaustive) Minimax."""
    check_root(game, state)
    max_player = game.to_move(state)
    counter = {"nodes": 1, "cutoffs": 0}          # 1 = the root
    start = time.perf_counter()
    best_move, best_value = None, -math.inf
    for a in game.actions(state):
        child = game.result(state, a)
        v = minimax(game, child, other(max_player), max_player, a, 1, max_depth, counter)
        if v > best_value:
            best_move, best_value = a, v
    elapsed = time.perf_counter() - start
    return SearchResult("minimax", best_move, best_value, counter["nodes"], elapsed, max_depth)


# --------------------------------------------------------------- Alpha-Beta
def alphabeta(game, state, player, max_player, last_move, depth, max_depth, alpha, beta,
              counter):
    counter["nodes"] += 1
    leaf = leaf_value(game, state, max_player, last_move, depth, max_depth)
    if leaf is not None:
        return leaf

    if player == max_player:                      # Max: raise alpha
        best = -math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = alphabeta(game, child, other(player), max_player, a, depth + 1, max_depth,
                          alpha, beta, counter)
            best = max(best, v)
            alpha = max(alpha, best)
            if alpha >= beta:                     # Min will never allow this branch
                counter["cutoffs"] += 1
                break
    else:                                         # Min: lower beta
        best = math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = alphabeta(game, child, other(player), max_player, a, depth + 1, max_depth,
                          alpha, beta, counter)
            best = min(best, v)
            beta = min(beta, best)
            if alpha >= beta:                     # Max will never allow this branch
                counter["cutoffs"] += 1
                break
    return best


def alphabeta_search(game, state, max_depth=None):
    """Best move for the player to move, by Minimax with Alpha-Beta pruning."""
    check_root(game, state)
    max_player = game.to_move(state)
    counter = {"nodes": 1, "cutoffs": 0}          # 1 = the root
    start = time.perf_counter()
    best_move, best_value = None, -math.inf
    alpha, beta = -math.inf, math.inf
    for a in game.actions(state):
        child = game.result(state, a)
        v = alphabeta(game, child, other(max_player), max_player, a, 1, max_depth,
                      alpha, beta, counter)
        if v > best_value:
            best_move, best_value = a, v
        alpha = max(alpha, best_value)
    elapsed = time.perf_counter() - start
    return SearchResult("alphabeta", best_move, best_value, counter["nodes"], elapsed,
                        max_depth, counter["cutoffs"])


ALGORITHMS = {
    "minimax": minimax_search,
    "alphabeta": alphabeta_search,
}
