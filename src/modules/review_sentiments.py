from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

import re
import math
import nltk
nltk.download('vader_lexicon', "stopwords")

class ReviewSentiments(BaseModule):
    def __init__(self):
        from nltk.sentiment import SentimentIntensityAnalyzer
        super().__init__()

        self.stopwords = nltk.corpus.stopwords.words("english")
        self.analyzer = SentimentIntensityAnalyzer()

    def run(self, data: Data, shared_data: Dict[str, Any]):
        listing_ids = data.reviews.listing_id.unique()

        # Ughh... Some csv data is broken...
        # Some records have text with multiline but does not include "" around the text...
        # Let's naively remove those by checking <br (as it is often present).
        listing_ids = [x for x in listing_ids if "<br" not in x]

        for i, listing_id in enumerate(listing_ids):
          percentage = (i / len(listing_ids)) * 100
          print(f"  Calculating review sentiments ({percentage:.2f}%)", end='\r')

          listing_reviews = data.reviews.loc[data.reviews['listing_id'] == listing_id]

          avg_sentiment = 0.0
          highest_sentiment = 0.0
          lowest_sentiment = 0.0

          for review in listing_reviews['comments']:
            if not isinstance(review, str):
              continue

            sentiment = self.get_sentiment(review)
            avg_sentiment += sentiment
            if sentiment > highest_sentiment:
              highest_sentiment = sentiment
            if sentiment < lowest_sentiment:
              lowest_sentiment = sentiment

          avg_sentiment /= len(listing_reviews)

          # TODO: Visualize the data

    def clean_review(self, review: str):
      cleaned = review.lower()
      cleaned = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", cleaned)

      cleaned = cleaned.replace("<br>", " ")
      cleaned = cleaned.replace("<br/>", " ")

      cleaned = " ".join([w for w in cleaned.split() if w not in (self.stopwords)])

      return cleaned

    def get_sentiment(self, review: str):
      cleaned_review = self.clean_review(review)
      return self.analyzer.polarity_scores(cleaned_review)['compound']