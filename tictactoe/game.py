"""
game.py - the Tic-Tac-Toe game engine for any N x N board and win length K.

State representation
--------------------
A state is a tuple of N*N cells, each 'X', 'O' or EMPTY ('.'), stored
row by row, so cell (r, c) is index r*N + c.  Tuples are immutable and
hashable, which makes states safe to share and usable as dict keys.
X always moves first, so whose turn it is follows from the counts.

Winning lines
-------------
Instead of hard-coding the 8 lines of 3x3, all lines are generated:
every horizontal, vertical, diagonal and anti-diagonal run of K cells.
For each cell we also keep the list of lines through it, so after a move
only those lines need to be checked.
"""
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
        self.lines = self._generate_lines()           # every winning line (tuple of cells)
        self.lines_through = [                        # lines passing through each cell
            [line for line in self.lines if cell in line]
            for cell in range(self.n * self.n)
        ]

    # ---------------------------------------------------------------- lines
    def _generate_lines(self):
        n, k = self.n, self.k
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # → ↓ ↘ ↙
        lines = []
        for r in range(n):
            for c in range(n):
                for dr, dc in directions:
                    end_r, end_c = r + dr * (k - 1), c + dc * (k - 1)
                    if 0 <= end_r < n and 0 <= end_c < n:
                        lines.append(tuple((r + dr * i) * n + (c + dc * i)
                                           for i in range(k)))
        return lines

    # ---------------------------------------------------------------- state
    def initial_state(self):
        return (EMPTY,) * (self.n * self.n)

    def to_move(self, state):
        """Whose turn it is (X moves first)."""
        return X if state.count(X) == state.count(O) else O

    def actions(self, state):
        """Legal moves = indices of empty cells, in row-major order."""
        return [i for i, cell in enumerate(state) if cell == EMPTY]

    def result(self, state, move):
        """Successor state after the player to move plays `move`."""
        if state[move] != EMPTY:
            raise ValueError(f"cell {move} is already occupied")
        cells = list(state)
        cells[move] = self.to_move(state)
        return tuple(cells)

    # ------------------------------------------------------------- terminal
    def is_win_at(self, state, cell):
        """Does the mark on `cell` complete a line? (fast check after a move)"""
        mark = state[cell]
        if mark == EMPTY:
            return False
        return any(all(state[i] == mark for i in line)
                   for line in self.lines_through[cell])

    def winner(self, state):
        """'X' or 'O' if that player has K in a line, else None."""
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

    # -------------------------------------------------------------- display
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
