"""
play.py - console interface: you vs the AI.
(AI vs AI is a mode in the GUI: python -m tictactoe.gui)

Examples
    python -m tictactoe.play                         # you (X) vs Alpha-Beta on 3x3
    python -m tictactoe.play --human O --algo minimax
    python -m tictactoe.play --size 4 --win 4 --depth 3
Defaults come from tictactoe/config.py.
"""
import argparse

from . import config
from .agents import HumanAgent, SearchAgent, play_game
from .config import GameSettings
from .game import TicTacToe, X, O


def build_settings(args) -> GameSettings:
    size = args.size
    win = args.win if args.win is not None else min(config.WIN_LENGTH, size)
    depth = args.depth
    if depth is None and size > 3:
        depth = config.LARGE_BOARD_DEFAULT_DEPTH
    if depth == 0:
        depth = None
    return GameSettings(size, win, depth)


def describe(agent) -> str:
    return agent.name


def main(argv=None):
    p = argparse.ArgumentParser(description="Tic-Tac-Toe with Minimax / Alpha-Beta")
    p.add_argument("--size", type=int, default=config.BOARD_SIZE, help="board size N")
    p.add_argument("--win", type=int, default=None, help="win length K (default from config)")
    p.add_argument("--depth", type=int, default=config.SEARCH_DEPTH,
                   help="search depth in plies (0 = full search)")
    p.add_argument("--algo", choices=["minimax", "alphabeta"], default="alphabeta",
                   help="algorithm for the AI")
    p.add_argument("--human", choices=[X, O], default=X, help="your side")
    args = p.parse_args(argv)

    settings = build_settings(args)
    game = TicTacToe(settings)
    depth_txt = "full" if settings.max_depth is None else settings.max_depth
    print(f"\n{settings.board_size}x{settings.board_size} board, "
          f"{settings.win_length} in a row wins, search depth: {depth_txt}\n")

    ai = SearchAgent(args.algo, settings.max_depth)
    human = HumanAgent()
    agent_x, agent_o = (human, ai) if args.human == X else (ai, human)

    def on_move(state, move, player):
        agent = agent_x if player == X else agent_o
        line = f"{player} plays {move}"
        if isinstance(agent, SearchAgent):
            r = agent.history[-1]
            line += (f"   [{r.algorithm}: value {r.value:+.3f}, "
                     f"{r.nodes:,} nodes, {r.time_s * 1000:.1f} ms]")
        print(line)
        print(game.render(state), "\n", flush=True)

    print(game.render(game.initial_state()), "\n")
    record = play_game(game, agent_x, agent_o, on_move=on_move)
    if record.winner is None:
        print("Result: draw")
    else:
        winner_agent = agent_x if record.winner == X else agent_o
        print(f"Result: {record.winner} ({describe(winner_agent)}) wins")


if __name__ == "__main__":
    main()
