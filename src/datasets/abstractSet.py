import pandas as pd  # type: ignore


class AbstractSet:
    def __init__(self):
        self.hlyByDayDF = None
        self.hlyByWeekDF = None
        self.hlyByMonthDF = None
        self.moistureByDayDF = None
        self.moistureByWeekDF = None
        self.moistureByMonthDF = None
        self.soilDF = None
        self.ergotDF = None


    def setHlyByDay(self, hlyByDayDF: pd.DataFrame):
        self.hlyByDayDF = hlyByDayDF

    def getHlyByDay(self) -> pd.DataFrame:
        return self.hlyByDayDF

    def setHlyByWeek(self, hlyByWeekDF: pd.DataFrame):
        self.hlyByWeekDF = hlyByWeekDF

    def getHlyByWeek(self) -> pd.DataFrame:
        return self.hlyByWeekDF

    def setHlyByMonth(self, hlyByMonthDF: pd.DataFrame):
        self.hlyByMonthDF = hlyByMonthDF

    def getHlyByMonth(self) -> pd.DataFrame:
        return self.hlyByMonthDF

    def setMoistureByDay(self, moistureByDayDF: pd.DataFrame):
        self.moistureByDayDF = moistureByDayDF

    def getMoistureByDay(self) -> pd.DataFrame:
        return self.moistureByDayDF

    def setMoistureByWeek(self, moistureByWeekDF: pd.DataFrame):
        self.moistureByWeekDF = moistureByWeekDF

    def getMoistureByWeek(self) -> pd.DataFrame:
        return self.moistureByWeekDF

    def setMoistureByMonth(self, moistureByMonthDF: pd.DataFrame):
        self.moistureByMonthDF = moistureByMonthDF

    def getMoistureByMonth(self) -> pd.DataFrame:
        return self.moistureByMonthDF

    def setSoil(self, soilDF: pd.DataFrame):
        self.soilDF = soilDF

    def getSoil(self) -> pd.DataFrame:
        return self.soilDF

    def setErgot(self, ergotDF: pd.DataFrame):
        self.ergotDF = ergotDF

    def getErgot(self) -> pd.DataFrame:
        return self.ergotDF

    def getCombinedDF(self, hlyByDay: bool, hlyByWeek: bool, hlyByMonth: bool, moistureByDay: bool, moistureByWeek: bool, moistureByMonth: bool, soil: bool) -> pd.DataFrame:
        combinedDF = self.ergotDF

        if hlyByDay:
            combinedDF = combinedDF.merge(self.hlyByDayDF, on=["year", "district"])
        if hlyByWeek:
            combinedDF = combinedDF.merge(self.hlyByWeekDF, on=["year", "district"])
        if hlyByMonth:
            combinedDF = combinedDF.merge(self.hlyByMonthDF, on=["year", "district"])
        if moistureByDay:
            combinedDF = combinedDF.merge(self.moistureByDayDF, on=["year", "district"])
        if moistureByWeek:
            combinedDF = combinedDF.merge(self.moistureByWeekDF, on=["year", "district"])
        if moistureByMonth:
            combinedDF = combinedDF.merge(self.moistureByMonthDF, on=["year", "district"])
        if soil:
            combinedDF = combinedDF.merge(self.soilDF, on=["district"])
