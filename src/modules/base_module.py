from typing import Dict, Any
from config import Config
from data_loader import Data

class BaseModule:
    def __init__(self):
        pass

    def set_config(self, cfg: Config):
        self.cfg = cfg

    def run(self, data: Data, shared_data: Dict[str, Any]):
        raise NotImplementedError