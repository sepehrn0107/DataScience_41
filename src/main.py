from config import Config
from data_loader import DataLoader
from pipeline import Pipeline
from modules import PrintData


def main():
    cfg = Config()
    
    dl = DataLoader(cfg)
    data = dl.load()

    pipe = Pipeline([
        PrintData(),
        # Add modules to run in sequence.
        # To add a new module just copy the PrintData module and modify the "run" function.
    ])

    pipe.run(cfg, data)

if __name__ == '__main__':
    main()