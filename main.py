"""Entry point: `python main.py` for the menu, or `python main.py gui|experiments|tests`."""
import sys

from tictactoe import experiments, gui, plots, report

MENU = """
============ Tic-Tac-Toe AI ============
 1. Play vs AI (window)
 2. Run experiments + charts
 3. Run tests
 0. Exit
========================================"""


def run_tests():
    print("\nRunning tests... (about half a minute)")
    return report.run_tests()


def run_experiments_and_charts():
    print("\nRunning experiments... (a minute or two)")
    experiments.main()
    plots.main()
    report.print_experiment_summary()


ACTIONS = {
    "gui": gui.main,
    "experiments": run_experiments_and_charts,
    "tests": run_tests,
}
NUMBERS = {"1": "gui", "2": "experiments", "3": "tests"}


def main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name not in ACTIONS:
            sys.exit(f"Unknown option {name!r}. Choose from: {', '.join(ACTIONS)}")
        ACTIONS[name]()
        return
    while True:
        print(MENU)
        try:
            choice = input("Choose an option: ").strip()
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
            if choice != "1":
                try:
                    input("\nPress Enter to return to the menu...")
                except (EOFError, KeyboardInterrupt):
                    break
        else:
            print("Please enter a number from the menu.")


if __name__ == "__main__":
    main()
