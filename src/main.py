from config import Config
from setup import setup
from data_loader import DataLoader
from pipeline import Pipeline

import modules


def main():
    cfg = Config()
    setup(cfg)

    dl = DataLoader(cfg)
    data = dl.load()

    pipe = Pipeline(
        [
            modules.PrintData(),
            modules.ReviewCleaning(),
            modules.ReviewSentiments(),
            modules.StaleListings(),
            modules.StayDurations(),
            # Add modules to run in sequence.
            # To add a new module just copy the PrintData module and modify the "run" function.
        ]
    )

    pipe.run(data)


if __name__ == "__main__":
    main()
