from abstractSet import AbstractSet
import pandas as pd


class Winter(AbstractSet):
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
        cols = df.columns.tolist()
        lastAttr = str(cols[len(cols) - 1])

        # Drops all column names based on the regular expression
        if lastAttr.find("-") != -1:  # This is a daily aggregate
            df = df[df.columns.drop(list(df.filter(regex="^0[3-9]-|^1[0-1]-")))]
        elif lastAttr.find("12:") != -1:  # This is a monthly aggregate
            df = df[df.columns.drop(list(df.filter(regex="^[3-9]:|^1[0-1]:")))]
        elif lastAttr.find("52:") != -1:  # This is a weekly aggregate
            df = df[df.columns.drop(list(df.filter(regex="^9:|^[1-3][0-9]:|^4[0-8]:")))]
        else:
            print("[ERROR] unexpected columns recieved in fall dataset")

        return df

    def _setHlyByDay(self, hlyByDayDF: pd.DataFrame):
        hlyByDayDF = self.selectData(hlyByDayDF)
        super()._setHlyByDay(hlyByDayDF)

    def _setHlyByWeek(self, hlyByWeekDF: pd.DataFrame):
        hlyByWeekDF = self.selectData(hlyByWeekDF)
        super()._setHlyByWeek(hlyByWeekDF)

    def _setHlyByMonth(self, hlyByMonthDF: pd.DataFrame):
        hlyByMonthDF = self.selectData(hlyByMonthDF)
        super()._setHlyByMonth(hlyByMonthDF)

    def _setMoistureByDay(self, moistureByDayDF: pd.DataFrame):
        moistureByDayDF = self.selectData(moistureByDayDF)
        super()._setMoistureByDay(moistureByDayDF)

    def _setMoistureByWeek(self, moistureByWeekDF: pd.DataFrame):
        moistureByWeekDF = self.selectData(moistureByWeekDF)
        super()._setMoistureByWeek(moistureByWeekDF)

    def _setMoistureByMonth(self, moistureByMonthDF: pd.DataFrame):
        moistureByMonthDF = self.selectData(moistureByMonthDF)
        super()._setMoistureByMonth(moistureByMonthDF)

    def _setSoil(self, soilDF: pd.DataFrame):
        super()._setSoil(soilDF)

    def _setErgot(self, ergotDF: pd.DataFrame):
        super()._setErgot(ergotDF)