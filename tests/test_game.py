"""Game-engine test: win detection on the two boards used in the project."""
import pytest

from tictactoe.config import GameSettings
from tictactoe.game import EMPTY, X, TicTacToe


@pytest.mark.parametrize("n,k,line_count", [(3, 3, 8), (4, 4, 10)])
def test_win_detection(n, k, line_count):
    """Every winning line is generated once; a full line wins, one mark short does not."""
    game = TicTacToe(GameSettings(n, k))
    assert len(game.lines) == line_count
    assert len(set(game.lines)) == line_count
    for line in game.lines:
        cells = [EMPTY] * (n * n)
        for i in line:
            cells[i] = X
        state = tuple(cells)
        assert game.winner(state) == X
        assert all(game.is_win_at(state, i) for i in line)

        cells[line[-1]] = EMPTY
        assert game.winner(tuple(cells)) is None
