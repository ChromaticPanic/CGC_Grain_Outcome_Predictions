# -------------------------------------------
# abstractSet.py
#
# After loading all datasets then aggregating them, the following class can be used to create exploratory datasets
#
# Aggregated data currently supported by this set:
#   - [hlyByDayDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/WeatherStation/hlyAggregator.py)
#   - [hlyByWeekDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/WeatherStation/hlyAggregator.py)
#   - [hlyByMonthDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/WeatherStation/hlyAggregator.py)
#   - [moistureByDayDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/SatelliteSoilMoisture/moistureAggregator.py)
#   - [moistureByWeekDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/SatelliteSoilMoisture/moistureAggregator.py)
#   - [moistureByMonthDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/SatelliteSoilMoisture/moistureAggregator.py)
#   - [soilDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/Soil/soilAggregator.py)
#   - [ergotDF](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/Ergot/ergotAggregator.py)
#
# Remarks:
#   - this is an abstract class, this means no instances can be created, rather its use is to reduce code duplication accross the other set classes
#
#   - new aggregated datasets can be added by adding the expected DataFrame to the constructor and creating similar getters/setters
#   - the columns bad ergot sets expect from input data to run properly are:
#       - year
#       - district
# -------------------------------------------
from abc import ABC, abstractmethod
import pandas as pd


class AbstractSet(ABC):
    def __init__(self):
        self.hlyByDayDF = None
        self.hlyByWeekDF = None
        self.hlyByMonthDF = None
        self.moistureByDayDF = None
        self.moistureByWeekDF = None
        self.moistureByMonthDF = None
        self.soilDF = None
        self.ergotDF = None

    @abstractmethod
    def selectData(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Purpose:
        This method is supposed to select data, however, since it is an abstract method it does nothing

        Remark: this method is necessary to ensure this class is abstract
        """
        pass

    def _setHlyByDay(self, hlyByDayDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by day)
        """
        self.hlyByDayDF = hlyByDayDF

    def getHlyByDay(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated hourly weather station data from the set (by day)

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.hlyByDayDF.drop(columns=["year", "district"])

    def _setHlyByWeek(self, hlyByWeekDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by week)
        """
        self.hlyByWeekDF = hlyByWeekDF

    def getHlyByWeek(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated hourly weather station data from the set (by week)

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.hlyByWeekDF.drop(columns=["year", "district"])

    def _setHlyByMonth(self, hlyByMonthDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by month)
        """
        self.hlyByMonthDF = hlyByMonthDF

    def getHlyByMonth(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated hourly weather station data from the set (by month)

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.hlyByMonthDF.drop(columns=["year", "district"])

    def _setMoistureByDay(self, moistureByDayDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by day)
        """
        self.moistureByDayDF = moistureByDayDF

    def getMoistureByDay(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated soil moisture data from the set (by day)

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.moistureByDayDF.drop(columns=["year", "district"])

    def _setMoistureByWeek(self, moistureByWeekDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by week)
        """
        self.moistureByWeekDF = moistureByWeekDF

    def getMoistureByWeek(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated soil moisture data from the set (by week)

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.moistureByWeekDF.drop(columns=["year", "district"])

    def _setMoistureByMonth(self, moistureByMonthDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by month)
        """
        self.moistureByMonthDF = moistureByMonthDF

    def getMoistureByMonth(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated soil moisture data from the set (by month)

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.moistureByMonthDF.drop(columns=["year", "district"])

    def _setSoil(self, soilDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil data into the set
        """
        self.soilDF = soilDF

    def getSoil(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated soil data from the set

        Pseudocode:
        - Return the DataFrame without the distrct attribute

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.soilDF.drop(columns=["district"])

    def _setErgot(self, ergotDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated ergot data into the set
        """
        self.ergotDF = ergotDF

    def getErgot(self) -> pd.DataFrame:
        """
        Purpose:
        Get the aggregated ergot data from the set

        Pseudocode:
        - Return the DataFrame without the year and distrct attributes

        Remarks: Since this change is not made inplace, it does not affect the data previously loaded
        """
        return self.ergotDF.drop(columns=["year", "district"])

    def getCombinedDF(
        self,
        hlyByDay: bool = False,
        hlyByWeek: bool = False,
        hlyByMonth: bool = False,
        moistureByDay: bool = False,
        moistureByWeek: bool = False,
        moistureByMonth: bool = False,
        soil: bool = False,
    ) -> pd.DataFrame:
        """
        Purpose:
        Fetches the selected subsets of data from the set (merged into a single DataFrame)

        Pseudocode:
        - Load the ergot data
        - For every other set, merge it into the DataFrame if it was selected
        - Return the DataFrame without the year and distrct attributes

        Remarks:
        - by default no sets are not selected
        - if no sets are selected, only the ergot data is returned
        """
        combinedDF = self.ergotDF.copy(deep=True)  # Load the ergot data

        # For every other set, merge it based on the year and or district if it was selected
        if hlyByDay:
            combinedDF = combinedDF.merge(self.hlyByDayDF, on=["year", "district"])
        if hlyByWeek:
            combinedDF = combinedDF.merge(self.hlyByWeekDF, on=["year", "district"])
        if hlyByMonth:
            combinedDF = combinedDF.merge(self.hlyByMonthDF, on=["year", "district"])
        if moistureByDay:
            combinedDF = combinedDF.merge(self.moistureByDayDF, on=["year", "district"])
        if moistureByWeek:
            combinedDF = combinedDF.merge(
                self.moistureByWeekDF, on=["year", "district"]
            )
        if moistureByMonth:
            combinedDF = combinedDF.merge(
                self.moistureByMonthDF, on=["year", "district"]
            )
        if soil:
            combinedDF = combinedDF.merge(self.soilDF, on=["district"])

        return combinedDF.drop(columns=["year", "district"])
