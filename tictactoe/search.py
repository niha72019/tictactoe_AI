"""Minimax and Minimax with Alpha-Beta pruning.
Both try moves in the same order, so Alpha-Beta always picks the same move as Minimax."""
import math
import time

from .config import DEPTH_PENALTY, DRAW_SCORE, WIN_SCORE
from .game import EMPTY, other
from .heuristics import evaluate


class SearchResult:
    def __init__(self, algorithm, move, value, nodes, time_s, max_depth, cutoffs=0):
        self.algorithm = algorithm
        self.move = move
        self.value = value
        self.nodes = nodes
        self.time_s = time_s
        self.max_depth = max_depth
        self.cutoffs = cutoffs


def leaf_value(game, state, max_player, last_move, depth, max_depth):
    """Value if the search must stop here (game over or depth limit), else None."""
    if game.is_win_at(state, last_move):
        # Lose a little per move made, so a quicker win (or a slower loss) scores better.
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


def minimax(game, state, player, max_player, last_move, depth, max_depth, counter):
    counter["nodes"] += 1
    leaf = leaf_value(game, state, max_player, last_move, depth, max_depth)
    if leaf is not None:
        return leaf

    # The AI (Max) picks the highest-valued move; its opponent (Min) picks the lowest.
    if player == max_player:
        best = -math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = minimax(game, child, other(player), max_player, a, depth + 1, max_depth, counter)
            best = max(best, v)
    else:
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
    counter = {"nodes": 1, "cutoffs": 0}          # 1 counts the root
    start = time.perf_counter()
    best_move, best_value = None, -math.inf
    for a in game.actions(state):
        child = game.result(state, a)
        v = minimax(game, child, other(max_player), max_player, a, 1, max_depth, counter)
        if v > best_value:
            best_move, best_value = a, v
    elapsed = time.perf_counter() - start
    return SearchResult("minimax", best_move, best_value, counter["nodes"], elapsed, max_depth)


def alphabeta(game, state, player, max_player, last_move, depth, max_depth, alpha, beta,
              counter):
    # alpha = best value Max is already sure of; beta = best value Min is already sure of.
    counter["nodes"] += 1
    leaf = leaf_value(game, state, max_player, last_move, depth, max_depth)
    if leaf is not None:
        return leaf

    if player == max_player:
        best = -math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = alphabeta(game, child, other(player), max_player, a, depth + 1, max_depth,
                          alpha, beta, counter)
            best = max(best, v)
            alpha = max(alpha, best)
            # Min already has a better option elsewhere and will never let the game
            # reach this position, so the remaining moves here can be skipped.
            if alpha >= beta:
                counter["cutoffs"] += 1
                break
    else:
        best = math.inf
        for a in game.actions(state):
            child = game.result(state, a)
            v = alphabeta(game, child, other(player), max_player, a, depth + 1, max_depth,
                          alpha, beta, counter)
            best = min(best, v)
            beta = min(beta, best)
            if alpha >= beta:                     # same cutoff, with Max's roles swapped
                counter["cutoffs"] += 1
                break
    return best


def alphabeta_search(game, state, max_depth=None):
    """Best move for the player to move, by Minimax with Alpha-Beta pruning."""
    check_root(game, state)
    max_player = game.to_move(state)
    counter = {"nodes": 1, "cutoffs": 0}          # 1 counts the root
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
