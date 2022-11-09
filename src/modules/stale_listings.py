from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data


# From trello:
#
# How can we identify apartment that are useless to Airbnb?
#
# This apartment can be score and reject from the platform. 
# They are not relevant for the platform and just nose in 
# the search results, and if a city complains about Airbnb, 
# this is a point that can be a pro in the discussion.
#
# - Listings they are no arable in the future, and they have 0 reviews over the last month
# - Host with a low response rate
# - Many automated reviews

class StaleListings(BaseModule):
    def __init__(self):
        super().__init__()

    def run(self, data: Data, shared_data: Dict[str, Any]):
        print("Hello from stale listings module.")
        