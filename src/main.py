"""
Entry point for the HIT137 Group Assignment 3 -
'Spot the Difference' desktop application.

Run with:
    python main.py
"""

from app import SpotTheDifferenceApp


def main() -> None:
    app = SpotTheDifferenceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
