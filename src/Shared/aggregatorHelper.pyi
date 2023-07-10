import pandas as pd  # type: ignore

class GenericQueryBuilder:
    def getDatesInYr(self) -> list: ...
    def getWeeksInYr(self) -> list: ...
    def getMonthsInYr(self) -> list: ...
    def reshapeDataByDates(
        self,
        dates: list,
        agg_df: pd.DataFrame,
        stationData: pd.DataFrame,
        dateType: str,
    ) -> pd.DataFrame: ...