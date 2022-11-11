from typing import Dict, Any
from data_loader import Data

from .base_module import BaseModule

import numpy as np
import pandas as pd


class CalculateVacancy(BaseModule):
    def __init__(self):
        pass

    def run(self, data: Data, shared_data: Dict[str, Any]):
        df = data.reviews.copy()

        lst_id_to_occupancy = df.groupby("listing_id").days_occupied.sum().reset_index()

        df = data.listings.copy()

        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
        df["first_review"] = pd.to_datetime(df["first_review"], errors="coerce")

        df["days_listed"] = df["last_review"] - df["first_review"]
        df["days_listed"] = df["days_listed"].dt.days

        df = df.merge(
            lst_id_to_occupancy.rename(columns={"listing_id": "id"}),
            on="id",
            how="left",
        )

        df["days_occupied"] = df[["days_occupied", "days_listed"]].min(axis=1)

        df["occupancy_percent"] = df["days_occupied"] / df["days_listed"]

        data.listings["vacancy_percent"] = 1 - df["occupancy_percent"]

        print(data.listings)

        # df.to_csv("vacancy_and_occupancy.csv")
        # data.reviews.to_csv("reviews_modified.csv")
