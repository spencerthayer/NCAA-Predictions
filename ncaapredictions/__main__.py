import argparse
from .core import command

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "year",
        help="The year you intend to make predictions for.")
    parser.add_argument(
        "data_path",
        help="The path to the folder with the relevant data."
    )
    args = parser.parse_args()
    command(args.year, args.data_path)
