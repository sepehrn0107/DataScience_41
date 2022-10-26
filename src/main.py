from config import Config
from data_loader import DataLoader


def main():
    cfg = Config()
    
    dl = DataLoader(cfg)
    data = dl.load()

if __name__ == '__main__':
    main()