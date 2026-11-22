"""
gui.py - Tkinter interface for Human-vs-AI and AI-vs-AI.

    python -m tictactoe.gui

Board size, win length, depth, algorithm and your side can be changed in
the panel; "New game" applies them. Defaults come from config.py.
The AI's search statistics are shown after each of its moves.
"""
import tkinter as tk
from tkinter import ttk

from . import config
from .agents import SearchAgent
from .config import GameSettings
from .game import TicTacToe, X, O, EMPTY

CELL_PX = 90
COLORS = {X: "#1f5fbf", O: "#c0392b", "win": "#ffe58a", "bg": "#fafafa"}


class TicTacToeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Tic-Tac-Toe — Minimax / Alpha-Beta")
        root.configure(bg=COLORS["bg"])

        panel = ttk.Frame(root, padding=8)
        panel.grid(row=0, column=0, sticky="ew")
        self.size_var = tk.IntVar(value=config.BOARD_SIZE)
        self.win_var = tk.IntVar(value=config.WIN_LENGTH)
        self.depth_var = tk.IntVar(value=config.SEARCH_DEPTH or 0)
        self.algo_var = tk.StringVar(value="alphabeta")
        self.mode_var = tk.StringVar(value="Human vs AI")
        self.side_var = tk.StringVar(value=X)

        def add(label, widget, col):
            ttk.Label(panel, text=label).grid(row=0, column=col, padx=(6, 2))
            widget.grid(row=0, column=col + 1)

        add("N", ttk.Spinbox(panel, from_=3, to=6, width=3, textvariable=self.size_var), 0)
        add("K", ttk.Spinbox(panel, from_=3, to=6, width=3, textvariable=self.win_var), 2)
        add("Depth (0=full)", ttk.Spinbox(panel, from_=0, to=16, width=3,
                                          textvariable=self.depth_var), 4)
        add("Algorithm", ttk.Combobox(panel, values=["alphabeta", "minimax"], width=10,
                                      state="readonly", textvariable=self.algo_var), 6)
        add("Mode", ttk.Combobox(panel, values=["Human vs AI", "AI vs AI"], width=11,
                                 state="readonly", textvariable=self.mode_var), 8)
        add("You play", ttk.Combobox(panel, values=[X, O], width=3, state="readonly",
                                     textvariable=self.side_var), 10)
        ttk.Button(panel, text="New game", command=self.new_game).grid(row=0, column=12, padx=8)

        self.canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=0, pady=8)
        self.canvas.bind("<Button-1>", self.on_click)
        self.status = ttk.Label(root, text="", padding=(8, 0, 8, 8), font=("Segoe UI", 11))
        self.status.grid(row=2, column=0, sticky="w")
        self.new_game()

    # ------------------------------------------------------------ game flow
    def new_game(self):
        n = max(3, self.size_var.get())
        k = min(max(3, self.win_var.get()), n)
        depth = self.depth_var.get() or None
        if depth is None and n > 3:   # full search is infeasible beyond 3x3
            depth = config.LARGE_BOARD_DEFAULT_DEPTH
            self.depth_var.set(depth)
        self.win_var.set(k)
        self.game = TicTacToe(GameSettings(n, k, depth))
        self.state = self.game.initial_state()
        self.ai = SearchAgent(self.algo_var.get(), depth)
        self.ai_vs_ai = self.mode_var.get() == "AI vs AI"
        self.human_side = self.side_var.get()
        self.game_id = getattr(self, "game_id", 0) + 1
        self.canvas.config(width=n * CELL_PX, height=n * CELL_PX)
        self.draw()
        self.set_status("Your move." if not self.ai_vs_ai and self.human_side == X else "AI thinking…")
        self.root.after(200, self.maybe_ai_move, self.game_id)

    def on_click(self, event):
        if self.ai_vs_ai or self.game.is_terminal(self.state):
            return
        if self.game.to_move(self.state) != self.human_side:
            return
        n = self.game.n
        r, c = event.y // CELL_PX, event.x // CELL_PX
        if not (0 <= r < n and 0 <= c < n):
            return
        move = r * n + c
        if self.state[move] != EMPTY:
            return
        self.state = self.game.result(self.state, move)
        self.draw()
        if not self.finish_if_over():
            self.set_status("AI thinking…")
            self.root.after(50, self.maybe_ai_move, self.game_id)

    def maybe_ai_move(self, game_id):
        if game_id != self.game_id or self.game.is_terminal(self.state):
            return
        if not self.ai_vs_ai and self.game.to_move(self.state) == self.human_side:
            return
        move = self.ai.choose_move(self.game, self.state)
        r = self.ai.history[-1]
        player = self.game.to_move(self.state)
        self.state = self.game.result(self.state, move)
        self.draw()
        if not self.finish_if_over():
            self.set_status(f"AI ({player}, {r.algorithm}) played {move}: value {r.value:+.3f}, "
                            f"{r.nodes:,} nodes, {r.time_s * 1000:.1f} ms")
            if self.ai_vs_ai:
                self.root.after(500, self.maybe_ai_move, game_id)

    def finish_if_over(self) -> bool:
        if not self.game.is_terminal(self.state):
            return False
        w = self.game.winner(self.state)
        if w is None:
            self.set_status("Draw!")
        elif self.ai_vs_ai:
            self.set_status(f"{w} wins!")
        else:
            self.set_status("You win!" if w == self.human_side else "AI wins!")
        return True

    # -------------------------------------------------------------- drawing
    def draw(self):
        cv, n = self.canvas, self.game.n
        cv.delete("all")
        line = self.game.winning_line(self.state) or ()
        for i, mark in enumerate(self.state):
            r, c = divmod(i, n)
            x0, y0 = c * CELL_PX, r * CELL_PX
            fill = COLORS["win"] if i in line else "white"
            cv.create_rectangle(x0, y0, x0 + CELL_PX, y0 + CELL_PX, fill=fill, outline="#888")
            if mark != EMPTY:
                cv.create_text(x0 + CELL_PX / 2, y0 + CELL_PX / 2, text=mark,
                               fill=COLORS[mark], font=("Segoe UI", int(CELL_PX * 0.45), "bold"))

    def set_status(self, text):
        self.status.config(text=text)


def main():
    root = tk.Tk()
    TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
