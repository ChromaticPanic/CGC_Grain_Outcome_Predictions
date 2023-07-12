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

        self._setHlyByDay(hlyByDayDF)
        self._setHlyByWeek(hlyByWeekDF)
        self._setHlyByMonth(hlyByMonthDF)
        self._setMoistureByDay(moistureByDayDF)
        self._setMoistureByWeek(moistureByWeekDF)
        self._setMoistureByMonth(moistureByMonthDF)
        self._setSoil(soilDF)
        self._setErgot(ergotDF)

    def selectData(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _setHlyByDay(self, hlyByDayDF: pd.DataFrame):
        super()._setHlyByDay(hlyByDayDF)

    def _setHlyByWeek(self, hlyByWeekDF: pd.DataFrame):
        super()._setHlyByWeek(hlyByWeekDF)

    def _setHlyByMonth(self, hlyByMonthDF: pd.DataFrame):
        super()._setHlyByMonth(hlyByMonthDF)

    def _setMoistureByDay(self, moistureByDayDF: pd.DataFrame):
        super()._setMoistureByDay(moistureByDayDF)

    def _setMoistureByWeek(self, moistureByWeekDF: pd.DataFrame):
        super()._setMoistureByWeek(moistureByWeekDF)

    def _setMoistureByMonth(self, moistureByMonthDF: pd.DataFrame):
        super()._setMoistureByMonth(moistureByMonthDF)

    def _setSoil(self, soilDF: pd.DataFrame):
        super()._setSoil(soilDF)

    def _setErgot(self, ergotDF: pd.DataFrame):
        super()._setErgot(ergotDF)
