"""
agents.py - players, and a function that plays one complete game.

SearchAgent  - picks every move by calling Minimax or Alpha-Beta search
               (no opening book, no hard-coded moves), and keeps a log of
               nodes/time for each move it makes.
RandomAgent  - the baseline: a uniformly random legal move (seeded RNG).
HumanAgent   - asks the user in the console.
"""
import random
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .game import State, TicTacToe, X, O
from .search import ALGORITHMS, SearchResult


class Agent:
    name = "agent"

    def choose_move(self, game: TicTacToe, state: State) -> int:
        raise NotImplementedError


class SearchAgent(Agent):
    def __init__(self, algorithm: str = "alphabeta", max_depth: Optional[int] = None):
        if algorithm not in ALGORITHMS:
            raise ValueError(f"unknown algorithm {algorithm!r}; choose from {list(ALGORITHMS)}")
        self.algorithm = algorithm
        self.search = ALGORITHMS[algorithm]
        self.max_depth = max_depth
        self.name = algorithm
        self.history: List[SearchResult] = []

    def choose_move(self, game: TicTacToe, state: State) -> int:
        result = self.search(game, state, self.max_depth)
        self.history.append(result)
        return result.move


class RandomAgent(Agent):
    name = "random"

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    def choose_move(self, game: TicTacToe, state: State) -> int:
        return self.rng.choice(game.actions(state))


class HumanAgent(Agent):
    name = "human"

    def __init__(self, input_fn: Callable[[str], str] = input):
        self.input_fn = input_fn

    def choose_move(self, game: TicTacToe, state: State) -> int:
        legal = game.actions(state)
        while True:
            text = self.input_fn(f"Your move ({game.to_move(state)}), cell number: ").strip()
            if text.isdigit() and int(text) in legal:
                return int(text)
            print(f"  Invalid. Choose one of: {legal}")


@dataclass
class GameRecord:
    winner: Optional[str]          # 'X', 'O' or None for a draw
    moves: List[int] = field(default_factory=list)
    final_state: Optional[State] = None


def play_game(game: TicTacToe, agent_x: Agent, agent_o: Agent,
              on_move: Optional[Callable[[State, int, str], None]] = None,
              start_state: Optional[State] = None) -> GameRecord:
    """Play until the game ends. `on_move(state, move, player)` is called after each move."""
    state = start_state if start_state is not None else game.initial_state()
    moves = []
    while not game.is_terminal(state):
        player = game.to_move(state)
        agent = agent_x if player == X else agent_o
        move = agent.choose_move(game, state)
        state = game.result(state, move)
        moves.append(move)
        if on_move:
            on_move(state, move, player)
    return GameRecord(game.winner(state), moves, state)


def outcome_for(record: GameRecord, side: str) -> str:
    """'win' / 'draw' / 'loss' from the point of view of `side`."""
    if record.winner is None:
        return "draw"
    return "win" if record.winner == side else "loss"


__all__ = ["Agent", "SearchAgent", "RandomAgent", "HumanAgent", "GameRecord",
           "play_game", "outcome_for", "X", "O"]
