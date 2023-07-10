import pandas as pd  # type: ignore


class AbstractSet:
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
        self.hlyByDayDF = hlyByDayDF
        self.hlyByWeekDF = hlyByWeekDF
        self.hlyByMonthDF = hlyByMonthDF
        self.moistureByDayDF = moistureByDayDF
        self.moistureByWeekDF = moistureByWeekDF
        self.moistureByMonthDF = moistureByMonthDF
        self.soilDF = soilDF
        self.ergotDF = ergotDF

    def getHlyByDay(self) -> pd.DataFrame:
        return self.hlyByDayDF

    def getHlyByWeek(self) -> pd.DataFrame:
        return self.hlyByWeekDF

    def getHlyByMonth(self) -> pd.DataFrame:
        return self.hlyByMonthDF

    def getMoistureByDay(self) -> pd.DataFrame:
        return self.moistureByDayDF

    def getMoistureByWeek(self) -> pd.DataFrame:
        return self.moistureByWeekDF

    def getMoistureByMonth(self) -> pd.DataFrame:
        return self.moistureByMonthDF

    def getSoil(self) -> pd.DataFrame:
        return self.soilDF

    def getErgot(self) -> pd.DataFrame:
        return self.ergotDF
