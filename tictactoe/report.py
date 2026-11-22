"""
report.py - the short, plain-English console output for the menu.

  print_experiment_summary()  one combined table built from results/summary.csv
  run_tests_with_checklist()  runs pytest quietly and prints one line per check

Neither function changes how the experiments or tests work; they only decide
what is printed.
"""
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from . import config
from .plots import node_saving_pct

ALGOS = ("minimax", "alphabeta")
ALGO_NAMES = {"minimax": "Minimax", "alphabeta": "Alpha-Beta"}


# --------------------------------------------------------------------------
# Option 3: experiments
# --------------------------------------------------------------------------
def setting_name(cfg: str) -> str:
    """'3x3 k3 full' -> '3x3, full search';  '4x4 k4 d3' -> '4x4, 4 in a row, depth 3'."""
    board, k, depth = cfg.split()
    parts = [board]
    if board != "3x3" or k != "k3":
        parts.append(f"{k[1:]} in a row")
    parts.append("full search" if depth == "full" else f"depth {depth[1:]}")
    return ", ".join(parts)


def ms(seconds: float) -> str:
    return f"{seconds * 1000:,.1f} ms" if seconds >= 0.0001 else "<0.1 ms"


def print_experiment_summary(results: Path = config.RESULTS_DIR) -> None:
    s = pd.read_csv(results / "summary.csv")
    configs = list(dict.fromkeys(s.config))
    by = s.set_index(["config", "algorithm"])

    # Each row: (label, {config: (minimax cell, alphabeta cell)} or {config: spanning cell})
    rows = []

    def per_algo(label, fmt):
        rows.append((label, {c: tuple(fmt(by.loc[(c, a)]) for a in ALGOS) for c in configs}))

    per_algo("Positions searched per move", lambda r: f"{r.mean_nodes:,.0f}")
    per_algo("Time per move", lambda r: ms(r.mean_time_s))
    per_algo("vs random player (W/D/L)",
             lambda r: f"{r.vs_random_win:.0f}/{r.vs_random_draw:.0f}/{r.vs_random_loss:.0f}")
    rows.append(("Same move chosen", {
        c: f"{round(by.loc[(c, 'minimax')].same_move_rate * by.loc[(c, 'minimax')].states)}"
           f" of {int(by.loc[(c, 'minimax')].states)} positions" for c in configs}))

    label_w = max(len(r[0]) for r in rows)
    col_w = max(10, *(len(c) for r in rows for v in r[1].values()
                      if isinstance(v, tuple) for c in v))
    group_w = 2 * col_w + 3
    group_w = max(group_w, *(len(setting_name(c)) for c in configs),
                  *(len(v) for r in rows for v in r[1].values() if isinstance(v, str)))
    col_w = (group_w - 3) // 2
    gap = "    "

    print()
    print(" " * label_w + gap + gap.join(setting_name(c).center(group_w) for c in configs))
    print(" " * label_w + gap + gap.join(
        (ALGO_NAMES["minimax"].rjust(col_w) + "   " + ALGO_NAMES["alphabeta"].rjust(col_w)).rjust(group_w)
        for _ in configs))
    print("-" * (label_w + len(configs) * (len(gap) + group_w)))
    for label, cells in rows:
        parts = []
        for c in configs:
            v = cells[c]
            if isinstance(v, tuple):
                parts.append((v[0].rjust(col_w) + "   " + v[1].rjust(col_w)).rjust(group_w))
            else:
                parts.append(v.center(group_w))
        print(label.ljust(label_w) + gap + gap.join(parts))

    saving = node_saving_pct(s)
    boards = [c.split()[0] for c in configs]
    names = {c: (b if boards.count(b) == 1 else setting_name(c)) for c, b in zip(configs, boards)}
    pieces = [f"{saving[c]:.0f}% fewer on {names[c]}" for c in configs]
    joined = pieces[0] if len(pieces) == 1 else ", ".join(pieces[:-1]) + " and " + pieces[-1]
    print(f"\nAlpha-Beta searched {joined}.".replace(" fewer on", " fewer positions on", 1))

    depth = pd.read_csv(results / "depth_scaling.csv")
    if not depth.empty:
        print("Depth comparison chart saved.")
    print(f"Charts saved to: {config.PLOTS_DIR}")


# --------------------------------------------------------------------------
# Option 4: tests
# --------------------------------------------------------------------------
# (plain-English description, test functions that make up this check)
CHECKS = [
    ("Win detection works on 3x3 and 4x4", ["test_win_detection"]),
    ("Minimax never loses on 3x3 (tried against every possible opponent move)",
     ["test_minimax_never_loses_against_any_opponent"]),
    ("Minimax vs Minimax always ends in a draw on 3x3", ["test_perfect_play_is_a_draw"]),
    ("AI takes a winning move and blocks the opponent's", ["test_takes_immediate_win_and_blocks"]),
    ("Alpha-Beta picks the same move as Minimax (every 3x3 position, and 4x4 at depth 3)",
     ["test_alphabeta_same_move_on_every_3x3_state", "test_alphabeta_same_move_depth_limited"]),
    ("Alpha-Beta searches fewer positions than Minimax", ["test_alphabeta_prunes_from_empty_board"]),
]


def run_tests_with_checklist() -> bool:
    """Run pytest exactly as before, hide its output, print one line per check."""
    project = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        xml_path = Path(tmp) / "results.xml"
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", f"--junitxml={xml_path}"],
                              cwd=project, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if not xml_path.exists():
            print("Tests could not be run. pytest said:\n")
            print(proc.stdout + proc.stderr)
            return False
        cases = list(ET.parse(xml_path).getroot().iter("testcase"))
        results = {}                       # test function -> list of failure messages
        for case in cases:
            name = case.get("name").split("[")[0]
            problems = [el.get("message") or el.tag for el in case
                        if el.tag in ("failure", "error")]
            results.setdefault(name, []).extend(problems)

    known = {f for _, funcs in CHECKS for f in funcs}
    checks = list(CHECKS) + [(f, [f]) for f in results if f not in known]   # never hide new tests
    failed = 0
    print()
    for description, funcs in checks:
        present = [f for f in funcs if f in results]
        problems = [p for f in present for p in results[f]]
        ok = bool(present) and not problems
        failed += not ok
        print(f"  {'✓' if ok else '✗'} {description}")
        if not present:
            print("      (test not found)")
        for p in problems[:1]:
            print(f"      {p.splitlines()[0][:110]}")

    total = len(checks)
    print()
    if failed == 0 and proc.returncode == 0:
        print(f"All checks passed ({total} checks, {len(cases)} tests).")
        return True
    if failed == 0:      # every check passed but pytest still reported a problem
        print("pytest reported a problem outside the checks above:\n")
        print("\n".join((proc.stdout + proc.stderr).strip().splitlines()[-15:]))
        return False
    print(f"{failed} of {total} checks failed.")
    return False

