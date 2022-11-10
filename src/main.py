from config import Config
from data_loader import DataLoader
from pipeline import Pipeline
from modules import PrintData, VacancyCalc


def main():
    cfg = Config()

    dl = DataLoader(cfg)
    data = dl.load()

    pipe = Pipeline([
        PrintData(),
        # Add modules to run in sequence.
        # To add a new module just copy the PrintData module and modify the "run" function.
        VacancyCalc()
    ])

    pipe.run(data)


if __name__ == '__main__':
    main()
