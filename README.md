# Tic-Tac-Toe: An Unbeatable Game-Playing Agent (Minimax + Alpha-Beta)

AI Lab mini-project (26B15CS216). Every AI move is produced by Minimax or
Alpha-Beta search; there are no hard-coded moves or openings.

## Setup
```
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
```

## Run everything from one place
- **Double-click `run.bat`**, or run `.venv\Scripts\python main.py` in a terminal, to get a menu:
  1. Play vs AI (window; also has an AI vs AI mode) · 2. Run experiments + charts · 3. Run tests · 0. Exit
- Shortcuts without the menu: `python main.py gui | experiments | tests`.

## Run individual parts
| What | Command |
|---|---|
| Console, you vs AI | `python -m tictactoe.play` (`--human O`, `--algo minimax`) |
| 4x4 board | `python -m tictactoe.play --size 4 --win 4 --depth 3` |
| GUI (Tkinter): you vs AI, or AI vs AI | `python -m tictactoe.gui` (pick the mode in the window) |
| All experiments → CSV | `python -m tictactoe.experiments` (`--quick` for a short run) |
| Charts from the CSVs | `python -m tictactoe.plots` |
| Tests | `python -m pytest -q` |

## Settings
Board size, win length, search depth, seeds and experiment sizes are all in
[`tictactoe/config.py`](tictactoe/config.py).

## Modules
| File | Purpose |
|---|---|
| `config.py` | all settings (`GameSettings`: board size N, win length K, depth) |
| `game.py` | N×N engine: state, moves, generated winning lines, terminal test, utility |
| `heuristics.py` | open-line evaluation for depth-limited search |
| `search.py` | Minimax and Alpha-Beta with node counting and timing |
| `agents.py` | search agent, random baseline, human player, `play_game` |
| `play.py` | console game: you vs the AI |
| `gui.py` | Tkinter window: you vs AI, or AI vs AI |
| `experiments.py` | measured experiments → `results/*.csv` |
| `plots.py` | charts drawn from the CSVs → `results/plots/*.png` |
| `report.py` | the short console summary (menu options 2 and 3) |
| `tests/` | win detection on 3×3 and 4×4; Minimax never loses on 3×3 (exhaustive) and draws against itself; takes wins / blocks threats; Alpha-Beta picks the same move as Minimax while searching fewer positions |

## Results (in `results/`)
Experiments run on two settings: **3×3 with full search** and **4×4, 4 in a row,
depth 3**, plus a depth comparison on 4×4 (depths 1–4).
`state_comparison.csv`, `games_vs_random.csv`, `ai_vs_ai.csv`,
`depth_scaling.csv`, `summary.csv`, and `plots/`. All values are written by
`experiments.py`; re-running it regenerates them.
