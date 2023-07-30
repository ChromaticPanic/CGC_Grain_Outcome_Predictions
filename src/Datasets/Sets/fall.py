# -------------------------------------------
# fall.py
#
# After loading all datasets then aggregating them, the following class can be used to create exploratory datasets from the fall data
# Fall data appears in the following date ranges:
#   - Daily: September 1st - November 30th (inclsuive)
#   - Weekly: Week 33 - Week 48 (inclusive)
#   - Monthly: Month 9 - Month 11 (inclusive)
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
#   - the columns fall sets expect from input data to run properly are:
#       - year
#       - district
#       - The last column must adhere to the formats set by the aggregator classes (links above) i.e MO-DA:ATTRIBUTE, W:ATTRIBUTE, M:ATTRIBUTE
#
#   - empty DataFrames are provided so that there is more flexibility in loading datasets i.e not all of them need to be provided
#   - new aggregated datasets can be easily added by adding the datatype to the constructor and creating getters and setters like so
# -------------------------------------------
from abstractSet import AbstractSet
import pandas as pd


class Fall(AbstractSet):
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
        Selects data for the fall set

        Pseudocode:
        - Check if the DataFrame provided has any data (by default, we dont expect to load anything)
        - If so, get the columns
        - Load the last column...
            - If the data is from a daily aggregate we expect the following format: MO-DA:ATTRIBUTE
            - If the data is from a weekly aggregate we expect the folloing format: W:ATTRIBUTE
            - If the data is from a monthly aggregate we expect the following format: M:ATTRIBUTE
        - If the data is a daily aggregate drop anything that does not fall within the fall date range
        - If the data is a weekly aggregate drop anything that does not fall within the fall date range
        - If the data is a monthly aggregate drop anything that does not fall within the fall date range
        - If there is an error, print a message

        Remark: When identifying which aggregate was used 52 and 12 are used, this is because there are 52 weeks per year and 12 months per year
        """
        if len(df) > 0:
            cols = df.columns.tolist()
            lastAttr = str(cols[len(cols) - 1])

            # Drops all column names based on the following regular expressions
            if lastAttr.find("-") != -1:  # This is a daily aggregate
                df = df[df.columns.drop(list(df.filter(regex="^0[1-8]-|^12-")))]
            elif lastAttr.find("12:") != -1:  # This is a monthly aggregate
                df = df[df.columns.drop(list(df.filter(regex="^[1-8]:|^12:")))]
            elif lastAttr.find("52:") != -1:  # This is a weekly aggregate
                df = df[
                    df.columns.drop(
                        list(
                            df.filter(
                                regex="^[1-9]:|^[1-2][0-9]:|^3[0-2]:|^49:|^5[0-2]:"
                            )
                        )
                    )
                ]
            else:
                print("[ERROR] unexpected columns recieved in fall dataset")

        return df

    def _setHlyByDay(self, hlyByDayDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by day)
        """
        hlyByDayDF = self.selectData(hlyByDayDF)
        super()._setHlyByDay(hlyByDayDF)

    def _setHlyByWeek(self, hlyByWeekDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by week)
        """
        hlyByWeekDF = self.selectData(hlyByWeekDF)
        super()._setHlyByWeek(hlyByWeekDF)

    def _setHlyByMonth(self, hlyByMonthDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated hourly weather station data into the set (by month)
        """
        hlyByMonthDF = self.selectData(hlyByMonthDF)
        super()._setHlyByMonth(hlyByMonthDF)

    def _setMoistureByDay(self, moistureByDayDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by day)
        """
        moistureByDayDF = self.selectData(moistureByDayDF)
        super()._setMoistureByDay(moistureByDayDF)

    def _setMoistureByWeek(self, moistureByWeekDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by week)
        """
        moistureByWeekDF = self.selectData(moistureByWeekDF)
        super()._setMoistureByWeek(moistureByWeekDF)

    def _setMoistureByMonth(self, moistureByMonthDF: pd.DataFrame):
        """
        Purpose:
        Load the aggregated soil moisture data into the set (by month)
        """
        moistureByMonthDF = self.selectData(moistureByMonthDF)
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
