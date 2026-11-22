"""
main.py - one entry point for the whole project.

    python main.py            # interactive menu
    python main.py gui | experiments | tests
"""
import contextlib
import io
import sys

from tictactoe import experiments, gui, plots, report

MENU = """
============ Tic-Tac-Toe AI ============
 1. Play vs AI (window)
 2. Run experiments + charts
 3. Run tests
 0. Exit
========================================"""


def run_tests() -> bool:
    print("\nRunning tests... (about a minute)")
    return report.run_tests_with_checklist()


def run_experiments_and_charts():
    print("\nRunning experiments... (a minute or two)")
    # the experiments and charts run exactly as before; only their
    # step-by-step progress output is hidden (all detail is in the CSVs)
    with contextlib.redirect_stdout(io.StringIO()):
        experiments.main([])
        plots.main()
    report.print_experiment_summary()


ACTIONS = {
    "gui": gui.main,
    "experiments": run_experiments_and_charts,
    "tests": run_tests,
}
NUMBERS = {"1": "gui", "2": "experiments", "3": "tests"}


def main():
    if hasattr(sys.stdout, "reconfigure"):      # never crash on ✓ / ✗ in an old console
        sys.stdout.reconfigure(errors="replace")
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name not in ACTIONS:
            sys.exit(f"Unknown option {name!r}. Choose from: {', '.join(ACTIONS)}")
        ACTIONS[name]()
        return
    while True:
        print(MENU)
        try:
            choice = input("Choose an option: ").strip().lstrip("﻿")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "0":
            break
        if choice in NUMBERS:
            try:
                ACTIONS[NUMBERS[choice]]()
            except KeyboardInterrupt:
                print("\n(stopped)")
            if choice != "1":   # keep the output on screen until the user is done reading
                try:
                    input("\nPress Enter to return to the menu...")
                except (EOFError, KeyboardInterrupt):
                    break
        else:
            print("Please enter a number from the menu.")


if __name__ == "__main__":
    main()
