import calendar
import datetime
import math
import re
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import Data

from .base_module import BaseModule


class VacancyCalc(BaseModule):
    AUTOMATED_MESSAGE = "This is an automated posting."

    def __init__(self):
        super().__init__()

    def run(self, data: Data, shared_data: Dict[str, Any]):
        df = data.reviews

        # Filter unecessary comments
        df = df[df["comments"].str.contains(
            self.AUTOMATED_MESSAGE) == False]

        # Merge to add minimyum_nights to each review for next step
        df = df.merge(data.listings[["id", "minimum_nights"]],
                      left_on="listing_id", right_on="id", how="left").drop(columns=["id_x", "id_y"])

        # Extract date from review text, otherwise use minimum definition
        df["nights"] = df[["comments", "minimum_nights"]].apply(
            lambda r: self.extract_duration(r[0]) or r[1], axis=1)

        # A few listings don't have any date, assume single day for these
        df["nights"] = df["nights"].fillna(1)

        print(df[["listing_id", "nights"]])

        # All columns are of type "object", which is not compatible with numeric operations
        # df["nights"] = pd.to_numeric(df["nights"])
        # df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d')

        # print(df.dtypes)

        # print(df[["listing_id", df["date"].dt.year]])

        # Attach year as column, can be useful for checking changes from year to year
        df['year'] = pd.DatetimeIndex(df['date']).year
        # df["year"] = pd.to_numeric(df["year"])

        df_vacancy = df.groupby(
            ["listing_id", df["year"]]).agg({"nights": np.sum})

        # df_vacancy.reset_index(level=1, inplace=True)
        # df_vacancy["leap"] = df_vacancy["year"].apply(
        #     lambda x: calendar.isleap(x))

        # df_vacancy["days_of_year"] = np.where(df_vacancy["leap"], 366, 365)
        # df_vacancy["vacancy"] = df_vacancy["days_of_year"] - \
        #     df_vacancy["nights"]
        # df_vacancy["vacancy"] = pd.to_numeric(df_vacancy["vacancy"])

        # print(df_vacancy["vacancy" > 366])

        # df = df.pivot_table(index="listing_id", columns="year",
        #                     values="nights", aggfunc=np.sum).fillna(0)

        print(df_vacancy)

        # df = df.pivot_table(index="date",
        #                     columns="listing_id",
        #                     values="nights",
        #                     aggfunc="first")

        # print(df)

        # year = 2019

        # df_2019 = pd.DataFrame()

        # df["date"] = pd.to_datetime(df["date"])

        # df_2019 = df[df["date"].dt.year == year]

        # print(df_2019 [["date", "nights", "comments"]])

    def extract_duration(self, review: str) -> int:
        r = re.compile("(\d+)\s(\w+)")

        valid = {"month": 30,
                 "week": 7,
                 "day": 1,
                 "night": 1}

        res = r.findall(review)

        for hit in res:
            clean_hit = hit[1].rstrip("s")

            if clean_hit in valid:
                return int(hit[0]) * valid[clean_hit]

        return None
