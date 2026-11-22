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
"""
import math
import time
from dataclasses import dataclass
from typing import Callable, Optional

from .config import DEPTH_PENALTY, DRAW_SCORE, WIN_SCORE
from .game import EMPTY, State, TicTacToe, other
from .heuristics import evaluate as default_evaluate

EvalFn = Callable[[TicTacToe, State, str], float]


@dataclass
class SearchResult:
    algorithm: str
    move: int                 # chosen cell index
    value: float              # backed-up value of the root for the player to move
    nodes: int                # number of states visited (root included)
    time_s: float             # wall-clock search time in seconds
    max_depth: Optional[int]
    cutoffs: int = 0          # number of prunings (Alpha-Beta only)


class _Searcher:
    """Shared machinery: node counter, terminal test and depth cut-off."""

    def __init__(self, game: TicTacToe, max_depth: Optional[int], evaluate_fn: EvalFn):
        self.game = game
        self.max_depth = max_depth
        self.evaluate_fn = evaluate_fn
        self.nodes = 0
        self.cutoffs = 0
        self.max_player = None

    def leaf_value(self, state: State, last_move: Optional[int], ply: int) -> Optional[float]:
        """Value if the search must stop here (terminal or depth limit), else None."""
        if last_move is not None and self.game.is_win_at(state, last_move):
            score = WIN_SCORE - DEPTH_PENALTY * ply
            return score if state[last_move] == self.max_player else -score
        if EMPTY not in state:
            return DRAW_SCORE
        if self.max_depth is not None and ply >= self.max_depth:
            return self.evaluate_fn(self.game, state, self.max_player)
        return None

    def check_root(self, state: State):
        if self.game.is_terminal(state):
            raise ValueError("cannot search from a terminal state")
        self.max_player = self.game.to_move(state)


# ------------------------------------------------------------------ Minimax
class _Minimax(_Searcher):
    def value(self, state: State, player: str, last_move: Optional[int], ply: int) -> float:
        self.nodes += 1
        leaf = self.leaf_value(state, last_move, ply)
        if leaf is not None:
            return leaf
        game = self.game
        if player == self.max_player:
            best = -math.inf
            for a in game.actions(state):
                best = max(best, self.value(game.result(state, a), other(player), a, ply + 1))
        else:
            best = math.inf
            for a in game.actions(state):
                best = min(best, self.value(game.result(state, a), other(player), a, ply + 1))
        return best


def minimax_search(game: TicTacToe, state: State, max_depth: Optional[int] = None,
                   evaluate_fn: EvalFn = default_evaluate) -> SearchResult:
    """Best move for the player to move, by plain (exhaustive) Minimax."""
    s = _Minimax(game, max_depth, evaluate_fn)
    s.check_root(state)
    start = time.perf_counter()
    s.nodes = 1                                     # the root
    best_move, best_value = None, -math.inf
    opponent = other(s.max_player)
    for a in game.actions(state):
        v = s.value(game.result(state, a), opponent, a, 1)
        if v > best_value:
            best_move, best_value = a, v
    elapsed = time.perf_counter() - start
    return SearchResult("minimax", best_move, best_value, s.nodes, elapsed, max_depth)


# --------------------------------------------------------------- Alpha-Beta
class _AlphaBeta(_Searcher):
    def value(self, state: State, player: str, last_move: Optional[int], ply: int,
              alpha: float, beta: float) -> float:
        self.nodes += 1
        leaf = self.leaf_value(state, last_move, ply)
        if leaf is not None:
            return leaf
        game = self.game
        if player == self.max_player:
            best = -math.inf
            for a in game.actions(state):
                best = max(best, self.value(game.result(state, a), other(player), a,
                                            ply + 1, alpha, beta))
                alpha = max(alpha, best)
                if alpha >= beta:          # Min will never allow this branch
                    self.cutoffs += 1
                    break
        else:
            best = math.inf
            for a in game.actions(state):
                best = min(best, self.value(game.result(state, a), other(player), a,
                                            ply + 1, alpha, beta))
                beta = min(beta, best)
                if alpha >= beta:          # Max will never allow this branch
                    self.cutoffs += 1
                    break
        return best


def alphabeta_search(game: TicTacToe, state: State, max_depth: Optional[int] = None,
                     evaluate_fn: EvalFn = default_evaluate) -> SearchResult:
    """Best move for the player to move, by Minimax with Alpha-Beta pruning."""
    s = _AlphaBeta(game, max_depth, evaluate_fn)
    s.check_root(state)
    start = time.perf_counter()
    s.nodes = 1
    best_move, best_value = None, -math.inf
    alpha, beta = -math.inf, math.inf
    opponent = other(s.max_player)
    for a in game.actions(state):
        v = s.value(game.result(state, a), opponent, a, 1, alpha, beta)
        if v > best_value:
            best_move, best_value = a, v
        alpha = max(alpha, best_value)
    elapsed = time.perf_counter() - start
    return SearchResult("alphabeta", best_move, best_value, s.nodes, elapsed,
                        max_depth, s.cutoffs)


ALGORITHMS = {
    "minimax": minimax_search,
    "alphabeta": alphabeta_search,
}
