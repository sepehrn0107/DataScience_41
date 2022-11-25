from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

from plotting import plot_path
import matplotlib.pyplot as plt


class ListingInfoPlots(BaseModule):
    # Additional constructor arguments can be added, like config etc.
    def __init__(self):
        super().__init__()

    # data is the airbnb dataset
    # items in shared_data can be set by any module and will be available to modules later in the pipeline.
    def run(self, data: Data, shared_data: Dict[str, Any]):
        listings = data.listings.copy()

        listings.dropna(
            subset=["host_response_rate", "host_acceptance_rate"], inplace=True
        )

        for col in ["host_response_rate", "host_acceptance_rate"]:
            listings[col] = listings[col].str.replace("%", "").astype(float)

        listings["price"] = listings["price"].str.replace(r"[$,]", "").astype(float)
        listings["longitude"] = listings["longitude"].astype(float)
        listings["latitude"] = listings["latitude"].astype(float)
        listings["minimum_nights"] = listings["minimum_nights"].astype(float)

        listings = listings[listings["latitude"] < 90]
        listings = listings[listings["longitude"] < 180]

        for col in [
            "review_scores_rating",
            "review_scores_accuracy",
            "review_scores_cleanliness",
            "review_scores_checkin",
            "review_scores_communication",
            "review_scores_location",
            "review_scores_value",
        ]:
            listings[col] = listings[col].astype(float)

        listings = listings.sort_values(by="vacancy_percent", ascending=False)

        # Plot vacancy_percent vs host_response_rate
        listings.plot.scatter(
            x="host_response_rate",
            y="vacancy_percent",
            ylabel="vacancy",
            xlabel="host response rate",
            color='#FF5A60',
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city,
                "vacancy_vs_host_response_rate",
            )
        )
        plt.close()

        # Plot vacancy_percent vs host_acceptance_rate
        listings.plot.scatter(
            x="host_acceptance_rate",
            y="vacancy_percent",
            ylabel="vacancy",
            xlabel="host acceptance rate",
            color='#FF5A60',
            figsize=(12, 8),
        ).get_figure().savefig(
            plot_path(
                data.city,
                "vacancy_vs_host_acceptance_rate",
            )
        )
        plt.close()

        # Plot the vacancy against neighbourhood
        listings.groupby("neighbourhood_cleansed").vacancy_percent.mean().plot.barh(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="neighbourhood",
            ylabel="neighbourhood",
            xlabel="vacancy"
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_neighbourhood"))
        plt.close()

        # Plot the vacancy against room_type
        listings.groupby("room_type").vacancy_percent.mean().plot.barh(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="room type",
            ylabel="room type",
            xlabel="vacancy"
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_room_type"))
        plt.close()

        # Plot the vacancy against instant_bookable
        listings.groupby("instant_bookable").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="instant_bookable",
            xlabel="instant bookable",
            ylabel="vacancy"
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_instant_bookable"))
        plt.close()

        # Plot the vacancy against accommodates
        listings.groupby("accommodates").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="accommodates",
            ylabel="vacancy",
            xlabel="accommodates"
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_accommodates"))
        plt.close()

        # Plot the vacancy against bedrooms
        listings.groupby("bedrooms").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="bedrooms",
            ylabel="vacancy",
            xlabel="bedrooms"
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_bedrooms"))
        plt.close()

        # Plot the vacancy against beds
        listings.groupby("beds").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="beds",
            ylabel="vacancy",
            xlabel="beds",
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_beds"))
        plt.close()

        # Plot the vacancy against price
        listings.plot.scatter(
            x="price",
            color='#FF5A60',
            y="vacancy_percent",
            logx=True,
            figsize=(12, 8),
            ylabel="vacancy",
            xlabel="price",
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_price"))
        plt.close()

        # Plot the vacancy against host_is_superhost
        listings.groupby("host_is_superhost").vacancy_percent.mean().plot.bar(
            figsize=(12, 8),
            color='#FF5A60',
            x="vacancy",
            y="host_is_superhost",
            xlabel="host is superhost",
            ylabel="vacancy",
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_host_is_superhost"))
        plt.close()

        # plot vacancy vs location
        listings.plot.scatter(
            x="longitude",
            y="latitude",
            xlabel="longitude",
            ylabel="latitude",
            s=8,
            c="vacancy_percent",
            cmap="cool_r",
            figsize=(10, 10),
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_location"))
        plt.close()

        # plot vacancy vs min nights
        listings.groupby("minimum_nights").vacancy_percent.mean().plot.line(
            x="minimum_nights",
            color='#FF5A60',
            y="vacancy_percent",
            xlabel="minimum nights",
            ylabel="vacancy",
            logx=True,
            figsize=(20, 10),
        ).get_figure().savefig(plot_path(data.city, "vacancy_vs_minimum_nights"))
        plt.close()

        for col in [
            "review_scores_rating",
            "review_scores_accuracy",
            "review_scores_cleanliness",
            "review_scores_checkin",
            "review_scores_communication",
            "review_scores_location",
            "review_scores_value",
        ]:
            listings.plot.scatter(
                x=col,
                xlabel=col.replace("_", " "),
                ylabel="vacancy",
                y="vacancy_percent",
                figsize=(15, 10),
                color='#FF5A60',
            ).get_figure().savefig(plot_path(data.city, f"vacancy_vs_{col}.svg"))
            plt.close()
