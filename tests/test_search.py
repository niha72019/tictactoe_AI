"""
Search tests.

1. Minimax never loses on 3x3 - proved by exhaustion: the Minimax agent plays
   as X and as O against EVERY possible sequence of opponent moves.
2. Minimax vs Minimax is a draw, and the AI takes wins / blocks threats.
3. Alpha-Beta picks the same move (and value) as Minimax on every reachable
   non-terminal 3x3 state, and on sampled 4x4 depth-3 states, while never
   visiting more nodes.
"""
import random

import pytest

from tictactoe.agents import SearchAgent, play_game
from tictactoe.config import GameSettings
from tictactoe.game import O, X, TicTacToe, apply_moves
from tictactoe.search import alphabeta_search, minimax_search


def all_reachable_states(game):
    """Every state reachable from the empty board (5478 for 3x3)."""
    seen, stack = set(), [game.initial_state()]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        if not game.is_terminal(s):
            stack.extend(game.result(s, a) for a in game.actions(s))
    return seen


@pytest.fixture(scope="module")
def game3():
    return TicTacToe(GameSettings(3, 3, None))


@pytest.fixture(scope="module")
def reachable3(game3):
    return all_reachable_states(game3)


# ----------------------------------------------------------- never loses
@pytest.mark.parametrize("ai_side", [X, O])
def test_minimax_never_loses_against_any_opponent(game3, ai_side):
    """Walk the whole game tree: the opponent tries every legal move at every
    turn, Minimax answers each position. No branch may end in an AI loss."""
    ai_move_cache = {}       # the AI is deterministic; cache only to save time
    outcomes = {"win": 0, "draw": 0, "loss": 0}

    def explore(state):
        winner = game3.winner(state)
        if winner is not None or game3.is_full(state):
            key = "draw" if winner is None else ("win" if winner == ai_side else "loss")
            outcomes[key] += 1
            assert key != "loss", f"Minimax lost: {''.join(state)}"
            return
        if game3.to_move(state) == ai_side:
            if state not in ai_move_cache:
                ai_move_cache[state] = minimax_search(game3, state).move
            explore(game3.result(state, ai_move_cache[state]))
        else:
            for a in game3.actions(state):
                explore(game3.result(state, a))

    explore(game3.initial_state())
    assert outcomes["loss"] == 0
    assert outcomes["win"] + outcomes["draw"] > 0


def test_perfect_play_is_a_draw(game3):
    record = play_game(game3, SearchAgent("minimax"), SearchAgent("minimax"))
    assert record.winner is None


def test_takes_immediate_win_and_blocks(game3):
    s = apply_moves(game3, [0, 3, 1, 4])          # X: 0,1  O: 3,4 ; X to move
    assert minimax_search(game3, s).move == 2       # win now
    s = apply_moves(game3, [0, 4, 1])               # X threatens 2 ; O to move
    assert minimax_search(game3, s).move == 2       # block


# ------------------------------------------- Alpha-Beta == Minimax (3x3)
def test_alphabeta_same_move_on_every_3x3_state(game3, reachable3):
    checked = 0
    for s in reachable3:
        if game3.is_terminal(s):
            continue
        mm = minimax_search(game3, s)
        ab = alphabeta_search(game3, s)
        assert ab.move == mm.move, f"different move on {''.join(s)}"
        assert ab.value == pytest.approx(mm.value)
        assert ab.nodes <= mm.nodes
        checked += 1
    assert checked == 4520                          # non-terminal reachable states


def test_alphabeta_prunes_from_empty_board(game3):
    mm = minimax_search(game3, game3.initial_state())
    ab = alphabeta_search(game3, game3.initial_state())
    assert mm.nodes == 549946                       # the full Tic-Tac-Toe game tree
    assert ab.nodes < mm.nodes and ab.cutoffs > 0


# ------------------------------- Alpha-Beta == Minimax (4x4, depth-limited)
def test_alphabeta_same_move_depth_limited():
    n, k, depth = 4, 4, 3
    game = TicTacToe(GameSettings(n, k, depth))
    rng = random.Random(1000 + n * 10 + k + depth)
    tested = 0
    while tested < 60:
        s = game.initial_state()
        for _ in range(rng.randint(0, n * n - 2)):
            if game.is_terminal(s):
                break
            s = game.result(s, rng.choice(game.actions(s)))
        if game.is_terminal(s):
            continue
        mm = minimax_search(game, s, depth)
        ab = alphabeta_search(game, s, depth)
        assert ab.move == mm.move and ab.value == pytest.approx(mm.value)
        assert ab.nodes <= mm.nodes
        tested += 1
