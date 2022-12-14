import random
from typing import Dict, Any
from .base_module import BaseModule
from data_loader import Data

import pandas as pd
from durations_nlp import Duration
import spacy

import matplotlib.pyplot as plt
from plotting import plot_path

from cache import Cache


class StayDurations(BaseModule):
    def __init__(self):
        super().__init__()

        self.nlp = spacy.load("en_core_web_sm")

        self.text_to_numbers_dict = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "eleven": "11",
            "twelve": "12",
            "thirteen": "13",
            "fourteen": "14",
            "fifteen": "15",
            "sixteen": "16",
            "seventeen": "17",
            "eighteen": "18",
            "nineteen": "19",
            "twenty": "20",
        }

        self.text_to_days_dict = {
            "dayss": "days",
            "night": "days",
            "nights": "days",
        }

    def run(self, data: Data, shared_data: Dict[str, Any]):
        def gen_data():
            df = data.reviews

            df["nights"] = df.comments.swifter.progress_bar(
                desc="Calculating nights stayed from reviews"
            ).apply(lambda x: self.get_nights(x))

            return df

        # Re-assigned to the data.reviews
        data.reviews = Cache(data.city, "StayDuration", gen_data).get()

        night_distribution = self.get_night_distribution(data.reviews)

        # Lets plot for the report
        self.plot_night_distribution(data.city, night_distribution)

        data.reviews["estimated_nights"] = random.choices(
            list(night_distribution.keys()),
            weights=night_distribution.values(),
            k=len(data.reviews),
        )

        data.reviews["days_occupied"] = data.reviews["nights"].combine_first(
            data.reviews["estimated_nights"]
        )

        # TODO: Visualize the data

    def get_nights(self, text):
        if "automated" in text:
            return None

        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                return self.text_to_days(ent.text)
        return None

    def text_to_days(self, text: str):
        if "old" in text:
            # these are mostly "5 months old" sons/daughters
            return None

        try:
            duration = Duration(text)
        except:
            text = self.fix_text(text)

        # One extra time for good measure (it helps)
        try:
            duration = Duration(text)
        except:
            text = self.fix_text(text)

        try:
            duration = Duration(text)
        except:
            return None

        days = duration.to_days()
        if days < 2 or days > 200:
            return None

        return int(days)

    def fix_text(self, text: str):
        text = text.lower()

        for k, v in self.text_to_numbers_dict.items():
            text = text.replace(k, str(v))

        for k, v in self.text_to_days_dict.items():
            text = text.replace(k, v)

        return text

    def get_night_distribution(self, df: pd.DataFrame):
        df = df.dropna(subset=["nights"])
        return df.nights.groupby(df.nights).count().to_dict()

    def plot_night_distribution(self, city: str, probs: Dict[int, float]):
        fig, ax = plt.subplots()
        ax.bar(probs.keys(), probs.values())
        ax.set_xscale("log")
        plt.savefig(plot_path(city, "night_distribution.png"))
        plt.close()
        # where do we can change the color?
