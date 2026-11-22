"""
play.py - console interface: you vs the AI.
(AI vs AI is a mode in the GUI: python -m tictactoe.gui)

    python -m tictactoe.play

All settings come from tictactoe/config.py:
  BOARD_SIZE, WIN_LENGTH, SEARCH_DEPTH   the board and how deep the AI searches
  PLAY_HUMAN_SIDE                        "X" (you move first) or "O"
  PLAY_ALGORITHM                         "alphabeta" or "minimax"
"""
from . import config
from .agents import HumanAgent, SearchAgent, play_game
from .config import GameSettings
from .game import TicTacToe, X


def build_settings():
    size = config.BOARD_SIZE
    win = min(config.WIN_LENGTH, size)
    depth = config.SEARCH_DEPTH
    if depth is None and size > 3:   # full search is infeasible beyond 3x3
        depth = config.LARGE_BOARD_DEFAULT_DEPTH
    return GameSettings(size, win, depth)


def describe(agent):
    return agent.name


def main():
    settings = build_settings()
    game = TicTacToe(settings)
    depth_txt = "full" if settings.max_depth is None else settings.max_depth
    print(f"\n{settings.board_size}x{settings.board_size} board, "
          f"{settings.win_length} in a row wins, search depth: {depth_txt}\n")

    ai = SearchAgent(config.PLAY_ALGORITHM, settings.max_depth)
    human = HumanAgent()
    agent_x, agent_o = (human, ai) if config.PLAY_HUMAN_SIDE == X else (ai, human)

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
