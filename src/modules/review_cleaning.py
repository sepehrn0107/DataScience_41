from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

import re
import pandas as pd
import swifter

import nltk
nltk.download("stopwords", quiet=True)


class ReviewCleaning(BaseModule):
    def __init__(self):
        super().__init__()

        self.text_regex = re.compile(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?")
        self.break_line_regex = re.compile(r"<br>|<br/>")
        self.space_regex = re.compile(r"\s+")

        self.stopwords = nltk.corpus.stopwords.words("english")

    def run(self, data: Data, shared_data: Dict[str, Any]):
        print("Cleaning reviews.")

        df = data.reviews

        # Firstly, some of the csv data is broken...
        # Some records have text with multiline but does not include "" around the text...
        # Let's naively remove those by checking <br (as it is often present in these cases).
        print("Removing broken records.")
        df = df[df["listing_id"].str.contains("<br") == False]

        # Let's remove the reviews that are not strings.
        df = df[df.comments.swifter.progress_bar(
            desc="Removing non-string reviews"
        ).apply(lambda x: isinstance(x, str))]

        # Clean the reviews (remove stop-words, symbols, etc.)
        df["comments"] = df.comments.swifter.progress_bar(
            desc="Cleaning review text"
        ).apply(self.clean_review)

        # Add correct types
        df["date"] = pd.to_datetime(df["date"])

        # Re-assigned the cleaned data to the data.reviews
        data.reviews = df

    def clean_review(self, review: str):
        cleaned = review.lower()

        # Only allow letters, numbers, and spaces.
        cleaned = self.text_regex.sub(" ", cleaned)

        # Remove break lines.
        cleaned = self.break_line_regex.sub(" ", cleaned)

        # Remove extra spaces as a result of the above cleaning.
        cleaned = self.space_regex.sub(" ", cleaned)

        # Can be removed if we want to keep the stopwords.
        cleaned = " ".join([w for w in cleaned.split() if w not in (self.stopwords)])

        return cleaned
