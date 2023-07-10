import pandas as pd  # type: ignore
from abstractSet import AbstractSet


class BadErgot(AbstractSet):
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
        super().__init__(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )
