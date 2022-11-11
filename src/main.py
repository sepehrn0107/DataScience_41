from config import Config
from setup import setup
from data_loader import DataLoader
from pipeline import Pipeline
import random

import modules


random.seed(1337)


def main():
    cfg = Config()
    setup(cfg)

    dl = DataLoader(cfg)
    data = dl.load()

    pipe = Pipeline(
        [
            modules.PrintData(),
            modules.ReviewCleaning(),
            modules.StayDurations(),
            modules.CalculateVacancy(),
            modules.ReviewSentiments(),
            modules.StaleListings(),
            # Add modules to run in sequence.
            # To add a new module just copy the PrintData module and modify the "run" function.
        ]
    )

    pipe.run(data)


if __name__ == "__main__":
    main()
