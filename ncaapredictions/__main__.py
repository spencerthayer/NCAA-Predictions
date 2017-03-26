import argparse
from .core import command

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "year",
        help="The year you intend to make predictions for.")
    args = parser.parse_args()
    command(args.year)
