from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

import pandas as pd

# From trello:
#
# How can we identify apartment that are useless to Airbnb?
#
# This apartment can be score and reject from the platform. 
# They are not relevant for the platform and just nose in 
# the search results, and if a city complains about Airbnb, 
# this is a point that can be a pro in the discussion.
#
# - Listings they are no available in the future, and they have 0 reviews over the last month
# - Host with a low response rate
# - Many automated reviews

class StaleListings(BaseModule):
    def __init__(self):
        super().__init__()

    def run(self, data: Data, shared_data: Dict[str, Any]):
        print("Finding stale listings.")
        listings_with_low_future_availability = self.get_listings_with_low_future_availability(
            data.listings, data.calendars, months=1, threshold=0.1
        )

        listings_with_no_recent_reviews = self.get_listings_with_no_recent_reviews(
            data.listings, data.reviews, months=3
        )


    # returns the listings that are not available for threshold % of the next 30 days
    def get_listings_with_low_future_availability(self, listings: pd.DataFrame, calendar: pd.DataFrame, months: int, threshold: float) -> pd.DataFrame:
        print("  Finding low availability listings.")

        # local cleaning
        calendar["date"] = pd.to_datetime(calendar["date"])
        calendar["price"] = calendar["price"].str.replace(r"[$,]", "").astype(float)
        calendar["available"] = calendar["available"].str.lower() == "t"

        max_future_date = calendar['date'].min() + pd.DateOffset(months=months)

        future_bookings = calendar[calendar['date'] < max_future_date]

        # Get the number of days that are available for each listing
        available_days = future_bookings[future_bookings['available'] == True].groupby('listing_id').size()

        # Convert available_days to a proportion of the total number of days
        availabilities = available_days / (months * 30)

        # return listings with availability below the threshold
        return listings[listings['id'].isin(availabilities[availabilities <= threshold].index)]


    def get_listings_with_no_recent_reviews(self, listings: pd.DataFrame, reviews: pd.DataFrame, months: int):
        print("  Finding listings with no recent reviews.")

        # We can't use "today" as the data is for a defined date.
        # Let's use the date of the last written review and subtract the number of months.
        min_date = reviews['date'].max() - pd.DateOffset(months=months)

        reviews_last_month = reviews[reviews['date'] > min_date]

        # Return listings that does not appear in reviews_last_month
        return listings[~listings['id'].isin(reviews_last_month['listing_id'])]