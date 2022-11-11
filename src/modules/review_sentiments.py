from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

from cache import Cache

from plotting import plot_path

from matplotlib import cm, pyplot as plt
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon", quiet=True)


class ReviewSentiments(BaseModule):
    def __init__(self):
        super().__init__()

        self.analyzer = SentimentIntensityAnalyzer()

    def run(self, data: Data, shared_data: Dict[str, Any]):
        def generate_data():
            df = data.reviews

            df["sentiment"] = df.comments.swifter.progress_bar(
                desc="Calculating review sentiments"
            ).apply(lambda x: self.analyzer.polarity_scores(x)["compound"])

            return df

        # Re-assigned to the data.reviews
        data.reviews = Cache(data.city, "ReviewSentiments", generate_data).get()

        self.plot(data)

    def plot(self, data: Data):
        reviews = data.reviews
        listings = data.listings

        # Merge and process data
        avg_sentiments_per_listing = (
            reviews.groupby("listing_id").sentiment.mean().reset_index()
        )
        merged = pd.merge(
            listings,
            avg_sentiments_per_listing.rename(columns={"listing_id": "id"}),
            on="id",
            how="left",
        )

        merged["price"] = merged["price"].str.replace(r"[$,]", "").astype(float)
        merged["longitude"] = merged["longitude"].astype(float)
        merged["latitude"] = merged["latitude"].astype(float)

        merged = merged[merged["latitude"] < 90]
        merged = merged[merged["longitude"] < 180]
        merged = merged.sort_values(by="sentiment", ascending=False)

        merged["minimum_nights"] = merged["minimum_nights"].astype(float)

        # plot histogram
        reviews["sentiment"].hist(bins=100, figsize=(10, 5)).get_figure().savefig(
            plot_path(data.city, "review_sentiment_distribution")
        )
        plt.close()

        # plot sentiment vs price
        merged.plot.scatter(
            x="price", y="sentiment", figsize=(10, 10), logx=True
        ).get_figure().savefig(plot_path(data.city, "review_sentiment_vs_price"))
        plt.close()

        # plot sentiment vs room type
        merged.groupby("room_type").sentiment.mean().plot.bar(
            yerr=merged.groupby("room_type").sentiment.std(), capsize=4, rot=0
        ).get_figure().savefig(plot_path(data.city, "review_sentiment_vs_room_type"))
        plt.close()

        # plot sentiment vs location
        merged.plot.scatter(
            x="minimum_nights",
            y="sentiment",
            logx=True,
            figsize=(20, 10),
        ).get_figure().savefig(
            plot_path(data.city, "review_sentiment_vs_minimum_nights")
        )
        plt.close()

        # plot sentiment vs location
        merged.plot.scatter(
            x="longitude",
            y="latitude",
            s=8,
            c="sentiment",
            cmap=cm.get_cmap("cool_r"),
            figsize=(10, 10),
        ).get_figure().savefig(plot_path(data.city, "review_sentiment_vs_location"))
        plt.close()
