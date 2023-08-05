# -------------------------------------------
# complete.py
#
# After loading all datasets then aggregating them, the following class can be used to create exploratory datasets from all the data
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
#   - the columns bad ergot sets expect from input data to run properly are:
#       - year
#       - district
#
#   - empty DataFrames are provided so that there is more flexibility in loading datasets i.e not all of them need to be provided
#   - new aggregated datasets can be added by adding the expected DataFrame to the constructor and creating similar getters/setters
#     in both this set class as well as the [abstractSet class]()
# -------------------------------------------
import pandas as pd
import os

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

from abstractSet import AbstractSet  # type: ignore


class Complete(AbstractSet):
    def __init__(
        self,
        hlyByDayDF: pd.DataFrame = pd.DataFrame(),
        hlyByWeekDF: pd.DataFrame = pd.DataFrame(),
        hlyByMonthDF: pd.DataFrame = pd.DataFrame(),
        moistureByDayDF: pd.DataFrame = pd.DataFrame(),
        moistureByWeekDF: pd.DataFrame = pd.DataFrame(),
        moistureByMonthDF: pd.DataFrame = pd.DataFrame(),
        soilDF: pd.DataFrame = pd.DataFrame(),
        ergotDF: pd.DataFrame = pd.DataFrame(),
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
        """
        Purpose:
        This method is supposed to select data, however, in the complete set all data is used, therefore it does not do anything

        Remark: As a subclass of AbstractSet, this function needs to be implemented so please do not delete it!
        """
        return df

    def _setHlyByDay(self, hlyByDayDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by day)
        """
        super()._setHlyByDay(hlyByDayDF)

    def _setHlyByWeek(self, hlyByWeekDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by week)
        """
        super()._setHlyByWeek(hlyByWeekDF)

    def _setHlyByMonth(self, hlyByMonthDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by month)
        """
        super()._setHlyByMonth(hlyByMonthDF)

    def _setMoistureByDay(self, moistureByDayDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by day)
        """
        super()._setMoistureByDay(moistureByDayDF)

    def _setMoistureByWeek(self, moistureByWeekDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by week)
        """
        super()._setMoistureByWeek(moistureByWeekDF)

    def _setMoistureByMonth(self, moistureByMonthDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by month)
        """
        super()._setMoistureByMonth(moistureByMonthDF)

    def _setSoil(self, soilDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil data into the set
        """
        super()._setSoil(soilDF)

    def _setErgot(self, ergotDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated ergot data into the set
        """
        super()._setErgot(ergotDF)
