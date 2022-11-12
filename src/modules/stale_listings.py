from typing import Any, Dict

import pandas as pd
from data_loader import Data

from .base_module import BaseModule

from plotting import plot_path
import matplotlib.pyplot as plt


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
        listings_with_low_future_availability = (
            self.get_listings_with_low_future_availability(
                data.listings, data.calendars, months=1, threshold=0.1
            )
        )

        # Listings with no reviews the past "months"
        listings_with_no_recent_reviews = self.get_listings_with_no_recent_reviews(
            data.listings, data.reviews, months=3
        )

        # Listings that over the last "months" have had a cancellation-to-review rate above the "threshold"
        listings_likely_to_cancel = self.get_listings_likely_to_cancel(
            data.listings, data.reviews, months=24, threshold=0.5
        )

        self.plot(
            data,
            listings_with_low_future_availability,
            listings_with_no_recent_reviews,
            listings_likely_to_cancel,
        )

    # returns the listings that are not available for threshold % of the next 30 days
    def get_listings_with_low_future_availability(
        self,
        listings: pd.DataFrame,
        calendar: pd.DataFrame,
        months: int,
        threshold: float,
    ) -> pd.DataFrame:
        # local cleaning
        calendar["date"] = pd.to_datetime(calendar["date"])
        calendar["price"] = calendar["price"].str.replace(r"[$,]", "").astype(float)
        calendar["available"] = calendar["available"].str.lower() == "t"

        max_future_date = calendar["date"].min() + pd.DateOffset(months=months)

        future_bookings = calendar[calendar["date"] < max_future_date]

        # Get the number of days that are available for each listing
        available_days = (
            future_bookings[future_bookings["available"] == True]
            .groupby("listing_id")
            .size()
        )

        # Convert available_days to a proportion of the total number of days
        availabilities = available_days / (months * 30)

        # return listings with availability below the threshold
        return listings[
            listings["id"].isin(availabilities[availabilities <= threshold].index)
        ]

    def get_listings_with_no_recent_reviews(
        self, listings: pd.DataFrame, reviews: pd.DataFrame, months: int
    ):
        recent_reviews = self.get_recent_reviews(reviews, months)

        # Return listings that does not appear in recent_reviews
        return listings[~listings["id"].isin(recent_reviews["listing_id"])]

    def get_listings_likely_to_cancel(
        self,
        listings: pd.DataFrame,
        reviews: pd.DataFrame,
        months: int,
        threshold: float,
    ):
        recent_reviews = self.get_recent_reviews(reviews, months)

        # Get the number of cancellations for each listing
        num_reviews_per_listing = recent_reviews.groupby("listing_id").size()
        cancellations_per_listing = (
            recent_reviews[
                recent_reviews["comments"].str.contains("host canceled reservation")
            ]
            .groupby("listing_id")
            .size()
        )

        # Convert to a proportion of the total number of reviews
        cancellation_rates = cancellations_per_listing / num_reviews_per_listing
        cancellation_rates = cancellation_rates.dropna()

        # Return listings with cancellation rates above the threshold
        return listings[
            listings["id"].isin(
                cancellation_rates[cancellation_rates >= threshold].index
            )
        ]

    def get_recent_reviews(self, reviews: pd.DataFrame, months: int) -> pd.DataFrame:
        min_date = reviews["date"].max() - pd.DateOffset(months=months)
        return reviews[reviews["date"] > min_date]

    def plot(
        self,
        data: Data,
        listings_with_low_future_availability,
        listings_with_no_recent_reviews,
        listings_likely_to_cancel,
    ):
        df = data.listings.copy()

        # Plot the number of listings per characteristic
        plt.figure(figsize=(5, 5))
        plt.pie(
            [len(listings_with_low_future_availability), len(df)],
            colors=["blue", "gray"],
            autopct="%1.1f%%",
        )
        plt.savefig(plot_path(data.city, "listings_with_low_future_availability.png"))
        plt.close()
        plt.figure(figsize=(5, 5))
        plt.pie(
            [len(listings_with_no_recent_reviews), len(df)],
            colors=["blue", "gray"],
            autopct="%1.1f%%",
        )
        plt.savefig(plot_path(data.city, "listings_with_no_recent_reviews.png"))
        plt.close()
        plt.figure(figsize=(5, 5))
        plt.pie(
            [len(listings_likely_to_cancel), len(df)],
            colors=["blue", "gray"],
            autopct="%1.1f%%",
        )
        plt.savefig(plot_path(data.city, "listings_likely_to_cancel.png"))
        plt.close()

        # set 0 or 1 for each listing for each characteristic if exists
        df["has_low_future_availability"] = 0
        df.loc[
            df["id"].isin(listings_with_low_future_availability["id"]),
            "has_low_future_availability",
        ] = 1

        df["has_no_recent_reviews"] = 0
        df.loc[
            df["id"].isin(listings_with_no_recent_reviews["id"]),
            "has_no_recent_reviews",
        ] = 1

        df["is_likely_to_cancel"] = 0
        df.loc[
            df["id"].isin(listings_likely_to_cancel["id"]), "is_likely_to_cancel"
        ] = 1

        # Plot the characteristics against neighbourhood
        df.groupby(
            "neighbourhood_cleansed"
        ).has_low_future_availability.mean().plot.barh(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city, "listings_with_low_future_availability_vs_neighbourhood"
            )
        )
        plt.close()
        df.groupby("neighbourhood_cleansed").has_no_recent_reviews.mean().plot.barh(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_no_recent_reviews_vs_neighbourhood")
        )
        plt.close()
        df.groupby("neighbourhood_cleansed").is_likely_to_cancel.mean().plot.barh(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_neighbourhood")
        )
        plt.close()

        # Plot the characteristics against room_type
        df.groupby("room_type").has_low_future_availability.mean().plot.barh(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_low_future_availability_vs_room_type")
        )
        plt.close()
        df.groupby("room_type").has_no_recent_reviews.mean().plot.barh(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_no_recent_reviews_vs_room_type")
        )
        plt.close()
        df.groupby("room_type").is_likely_to_cancel.mean().plot.barh(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_room_type")
        )
        plt.close()

        # Plot the characteristics against instant_bookable
        df.groupby("instant_bookable").has_low_future_availability.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city, "listings_with_low_future_availability_vs_instant_bookable"
            )
        )
        plt.close()
        df.groupby("instant_bookable").has_no_recent_reviews.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_no_recent_reviews_vs_instant_bookable")
        )
        plt.close()
        df.groupby("instant_bookable").is_likely_to_cancel.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_instant_bookable")
        )
        plt.close()

        # Plot the characteristics against accommodates
        df.groupby("accommodates").has_low_future_availability.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city, "listings_with_low_future_availability_vs_accommodates"
            )
        )
        plt.close()
        df.groupby("accommodates").has_no_recent_reviews.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_no_recent_reviews_vs_accommodates")
        )
        plt.close()
        df.groupby("accommodates").is_likely_to_cancel.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_accommodates")
        )
        plt.close()

        # Plot the characteristics against bedrooms
        df.groupby("bedrooms").has_low_future_availability.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_low_future_availability_vs_bedrooms")
        )
        plt.close()
        df.groupby("bedrooms").has_no_recent_reviews.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_no_recent_reviews_vs_bedrooms")
        )
        plt.close()
        df.groupby("bedrooms").is_likely_to_cancel.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_bedrooms")
        )
        plt.close()

        # Plot the characteristics against beds
        df.groupby("beds").has_low_future_availability.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_low_future_availability_vs_beds")
        )
        plt.close()
        df.groupby("beds").has_no_recent_reviews.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_with_no_recent_reviews_vs_beds")
        )
        plt.close()
        df.groupby("beds").is_likely_to_cancel.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_beds")
        )
        plt.close()

        # Plot the characteristics against host_acceptance_rate
        df.groupby("host_acceptance_rate").has_low_future_availability.mean().plot.line(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city,
                "listings_with_low_future_availability_vs_host_acceptance_rate",
            )
        )
        plt.close()
        df.groupby("host_acceptance_rate").has_no_recent_reviews.mean().plot.line(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city, "listings_with_no_recent_reviews_vs_host_acceptance_rate"
            )
        )
        plt.close()
        df.groupby("host_acceptance_rate").is_likely_to_cancel.mean().plot.line(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(data.city, "listings_likely_to_cancel_vs_host_acceptance_rate")
        )
        plt.close()

        # plot vs vacancy percent
        df.groupby("has_low_future_availability").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city,
                "listings_with_low_future_availability_vs_vacancy",
            )
        )
        plt.close()
        df.groupby("has_no_recent_reviews").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city,
                "listings_with_no_recent_reviews_vs_vacancy",
            )
        )
        plt.close()
        df.groupby("is_likely_to_cancel").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city,
                "listings_likely_to_cancel_vs_vacancy",
            )
        )
        plt.close()
