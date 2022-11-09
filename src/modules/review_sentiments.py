from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

import re
import math
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)

class ReviewSentiments(BaseModule):
    def __init__(self):
        super().__init__()

        self.analyzer = SentimentIntensityAnalyzer()

    def run(self, data: Data, shared_data: Dict[str, Any]):
        df = data.reviews

        df["sentiment"] = df.comments.swifter.progress_bar(
            desc="Calculating review sentiments."
        ).apply(lambda x: self.analyzer.polarity_scores(x)['compound'])

        # Re-assigned to the data.reviews
        data.reviews = df
        
        # TODO: Visualize the data