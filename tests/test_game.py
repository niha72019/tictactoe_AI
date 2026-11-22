"""Game-engine test: win detection on the two boards used in the project."""
import pytest

from tictactoe.config import GameSettings
from tictactoe.game import EMPTY, X, TicTacToe


@pytest.mark.parametrize("n,k,line_count", [(3, 3, 8), (4, 4, 10)])
def test_win_detection(n, k, line_count):
    """All winning lines exist (rows + columns + 2 diagonals); every full line
    is a win (both win checks agree); one mark short is not."""
    game = TicTacToe(GameSettings(n, k))
    assert len(game.lines) == line_count
    assert len(set(game.lines)) == line_count          # no duplicates
    for line in game.lines:
        cells = [EMPTY] * (n * n)
        for i in line:
            cells[i] = X
        state = tuple(cells)
        assert game.winner(state) == X
        assert all(game.is_win_at(state, i) for i in line)

        cells[line[-1]] = EMPTY
        assert game.winner(tuple(cells)) is None
