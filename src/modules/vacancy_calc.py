from typing import Dict, Any
from data_loader import Data

from .base_module import BaseModule

import numpy as np


class CalculateVacancy(BaseModule):
    def __init__(self):
        pass

    def run(self, data: Data, shared_data: Dict[str, Any]):
        df = data.reviews.copy()

        df["days_occupied"] = df["nights"].combine_first(df["estimated_nights"])

        df_a = df.groupby("listing_id").days_occupied.sum().reset_index()
        df_b = df.groupby("listing_id").date.min().reset_index()
        df_c = df.groupby("listing_id").date.max().reset_index()

        df = df_a

        df["days_listed"] = df_c.date - df_b.date

        df["days_listed"] = df["days_listed"].dt.days

        df["days_listed"] = df[["days_occupied", "days_listed"]].max(axis=1)

        df["vacancy_percent"] = df["days_occupied"] / df["days_listed"]

        data.listings["vacancy_percent"] = df["vacancy_percent"]

        print(data.listings)

        # df.to_csv("vacancy_and_occupancy.csv")
        # data.reviews.to_csv("reviews_modified.csv")
