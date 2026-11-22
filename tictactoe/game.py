"""Tic-Tac-Toe rules for an N x N board where K in a row wins.
A state is a tuple of N*N cells ('X', 'O' or '.') stored row by row, so cell (r, c) is r*N + c."""
from .config import DEFAULT_SETTINGS

X, O, EMPTY = "X", "O", "."


def other(player):
    return O if player == X else X


class TicTacToe:
    """Rules of N x N Tic-Tac-Toe with win length K."""

    def __init__(self, settings=DEFAULT_SETTINGS):
        self.settings = settings
        self.n = settings.board_size
        self.k = settings.win_length
        self.lines = self._generate_lines()
        # Lines through each cell, so after a move only those need checking.
        self.lines_through = [
            [line for line in self.lines if cell in line]
            for cell in range(self.n * self.n)
        ]

    def _generate_lines(self):
        # From every cell, step K-1 times in each direction; if the last cell is
        # still on the board, those K cells form a winning line.
        n, k = self.n, self.k
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # right, down, down-right, down-left
        lines = []
        for r in range(n):
            for c in range(n):
                for dr, dc in directions:
                    end_r, end_c = r + dr * (k - 1), c + dc * (k - 1)
                    if 0 <= end_r < n and 0 <= end_c < n:
                        lines.append(tuple((r + dr * i) * n + (c + dc * i)
                                           for i in range(k)))
        return lines

    def initial_state(self):
        return (EMPTY,) * (self.n * self.n)

    def to_move(self, state):
        return X if state.count(X) == state.count(O) else O

    def actions(self, state):
        return [i for i, cell in enumerate(state) if cell == EMPTY]

    def result(self, state, move):
        if state[move] != EMPTY:
            raise ValueError(f"cell {move} is already occupied")
        cells = list(state)
        cells[move] = self.to_move(state)
        return tuple(cells)

    def is_win_at(self, state, cell):
        """Does the mark on `cell` complete a line? Checks only lines through `cell`."""
        mark = state[cell]
        if mark == EMPTY:
            return False
        return any(all(state[i] == mark for i in line)
                   for line in self.lines_through[cell])

    def winner(self, state):
        for line in self.lines:
            first = state[line[0]]
            if first != EMPTY and all(state[i] == first for i in line):
                return first
        return None

    def winning_line(self, state):
        for line in self.lines:
            first = state[line[0]]
            if first != EMPTY and all(state[i] == first for i in line):
                return line
        return None

    def is_full(self, state):
        return EMPTY not in state

    def is_terminal(self, state):
        return self.winner(state) is not None or self.is_full(state)

    def render(self, state):
        n = self.n
        width = len(str(n * n - 1))
        rows = []
        for r in range(n):
            cells = []
            for c in range(n):
                i = r * n + c
                cells.append(state[i].center(width) if state[i] != EMPTY
                             else str(i).rjust(width))
            rows.append(" " + " | ".join(cells))
        sep = "\n" + "-" * len(rows[0]) + "\n"
        return sep.join(rows)


def apply_moves(game, moves):
    state = game.initial_state()
    for m in moves:
        state = game.result(state, m)
    return state
