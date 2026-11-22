"""Players (search AI, random, human) and a function that plays one full game."""
import random

from .game import X, O
from .search import ALGORITHMS


class Agent:
    name = "agent"

    def choose_move(self, game, state):
        raise NotImplementedError


class SearchAgent(Agent):
    def __init__(self, algorithm="alphabeta", max_depth=None):
        if algorithm not in ALGORITHMS:
            raise ValueError(f"unknown algorithm {algorithm!r}; choose from {list(ALGORITHMS)}")
        self.algorithm = algorithm
        self.search = ALGORITHMS[algorithm]
        self.max_depth = max_depth
        self.name = algorithm
        self.history = []

    def choose_move(self, game, state):
        result = self.search(game, state, self.max_depth)
        self.history.append(result)
        return result.move


class RandomAgent(Agent):
    name = "random"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose_move(self, game, state):
        return self.rng.choice(game.actions(state))


class HumanAgent(Agent):
    name = "human"

    def __init__(self, input_fn=input):
        self.input_fn = input_fn

    def choose_move(self, game, state):
        legal = game.actions(state)
        while True:
            text = self.input_fn(f"Your move ({game.to_move(state)}), cell number: ").strip()
            if text.isdigit() and int(text) in legal:
                return int(text)
            print(f"  Invalid. Choose one of: {legal}")


class GameRecord:
    def __init__(self, winner, moves=None, final_state=None):
        self.winner = winner                              # None means a draw
        self.moves = moves if moves is not None else []
        self.final_state = final_state


def play_game(game, agent_x, agent_o, on_move=None, start_state=None):
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


def outcome_for(record, side):
    if record.winner is None:
        return "draw"
    return "win" if record.winner == side else "loss"


__all__ = ["Agent", "SearchAgent", "RandomAgent", "HumanAgent", "GameRecord",
           "play_game", "outcome_for", "X", "O"]
