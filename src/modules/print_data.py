from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

class PrintData(BaseModule):
    # Additional constructor arguments can be added.
    # self.cfg is not available in the constructor, but can be passed manually.
    def __init__(self):
        super().__init__()

    # data is the airbnb dataset
    # items in shared_data can be set by any module and will be available to modules later in the pipeline.
    def run(self, data: Data, shared_data: Dict[str, Any]):
        print("Listings:")
        print(data.listings, end="\n\n")

        print("Calendars:")
        print(data.calendars, end="\n\n")

        print("Reviews:")
        print(data.reviews, end="\n\n")