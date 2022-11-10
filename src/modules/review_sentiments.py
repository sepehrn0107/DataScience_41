from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

from cache import Cache

from plotting import plot_path

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

        # plot the distribution of sentiments
        reviews["sentiment"].hist(bins=100, figsize=(10, 5)).get_figure().savefig(
            plot_path(data.city, "review_sentiment_distribution")
        )
