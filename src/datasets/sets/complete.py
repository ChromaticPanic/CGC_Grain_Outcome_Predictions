from abstractSet import AbstractSet
import pandas as pd  # type: ignore


class Complete(AbstractSet):
    def __init__(
        self,
        hlyByDayDF: pd.DataFrame,
        hlyByWeekDF: pd.DataFrame,
        hlyByMonthDF: pd.DataFrame,
        moistureByDayDF: pd.DataFrame,
        moistureByWeekDF: pd.DataFrame,
        moistureByMonthDF: pd.DataFrame,
        soilDF: pd.DataFrame,
        ergotDF: pd.DataFrame,
    ):
        super().__init__()


        # all for weather by month
        # add for weather by week
        # all for weather by day

        # all for soil moisture and moisture by month
        # all for soil moisture and moisture by week
        # all for soil moisture and moisture by day

        # all for weather and soil moisture by month
        # all for weather and soil moisture and soil by month
        # add for weather and soil moisture by week
        # add for weather and soil moisture and soil by week
        # all for weather and soil moisture by day
        # all for weather and soil moisture and soil by day