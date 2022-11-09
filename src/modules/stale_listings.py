from typing import Any, Dict

import pandas as pd
from data_loader import Data

from .base_module import BaseModule

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

        # Listings that are less than "threshold" available for the next "months"
        listings_with_low_future_availability = self.get_listings_with_low_future_availability(
            data.listings, data.calendars, months=1, threshold=0.1
        )

        # Listings with no reviews the past "months"
        listings_with_no_recent_reviews = self.get_listings_with_no_recent_reviews(
            data.listings, data.reviews, months=3
        )

        # Listings that over the last "months" have had a cancellation-to-review rate above the "threshold"
        listings_likely_to_cancel = self.get_listings_likely_to_cancel(
            data.listings, data.reviews, months=24, threshold=0.5
        )

        # TODO: Visualize the data

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
        recent_reviews = self.get_recent_reviews(reviews, months)

        # Return listings that does not appear in recent_reviews
        return listings[~listings['id'].isin(recent_reviews['listing_id'])]

    def get_listings_likely_to_cancel(self, listings: pd.DataFrame, reviews: pd.DataFrame, months: int, threshold: float):
        print("  Finding listings with cancellations.")
        recent_reviews = self.get_recent_reviews(reviews, months)

        # Get the number of cancellations for each listing
        num_reviews_per_listing = recent_reviews.groupby('listing_id').size()
        cancellations_per_listing = recent_reviews[recent_reviews['comments'].str.contains('host canceled reservation')].groupby('listing_id').size()

        # Convert to a proportion of the total number of reviews
        cancellation_rates = cancellations_per_listing / num_reviews_per_listing
        cancellation_rates = cancellation_rates.dropna()

        # Return listings with cancellation rates above the threshold
        return listings[listings['id'].isin(cancellation_rates[cancellation_rates >= threshold].index)]

    def get_recent_reviews(self, reviews: pd.DataFrame, months: int) -> pd.DataFrame:
        min_date = reviews['date'].max() - pd.DateOffset(months=months)
        return reviews[reviews['date'] > min_date]