from typing import List, Dict, Any
from config import Config
from data_loader import Data

from modules.base_module import BaseModule

class Pipeline:
    def __init__(self, modules: List[BaseModule]):
        self.modules = modules
        self.shared_data: Dict[str, Any] = {}
    
    def run(self, data: Data):
        for module in self.modules:
            module.run(data, self.shared_data)
        
        # Cleanup shared data after running all modules.
        self.shared_data = {}