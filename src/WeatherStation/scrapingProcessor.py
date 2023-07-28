# ----------------------------------------------------
# DataProcessor.py
#
# Purpose: handles the more complex data processing and manipulations for station scraping:
# - scrapeDaily.py
# - scrapeHourlyParallel.py
# ----------------------------------------------------
from datetime import datetime
import numpy as np
import pandas as pd
import typing


class ScrapingProcessor:
    @typing.no_type_check  # need to define a data class for this
    def removeInactive(
        self, stations: pd.DataFrame, states: list) -> pd.DataFrame:
        """
        Purpose:
        Remove the inactive stations from the list of stations once pulled

        Pseudocode:
        - For each state, check if its active
        - If it is not active, remove it from the DataFrame

        Remarks: stations and states are both parallel
        """
        for state in states:
            if not state["is_active"]:
                stations.drop(
                    stations[stations.station_id == state["station_id"]].index,
                    inplace=True,
                )

        return stations

    @typing.no_type_check  # need to define a data class for this
    def addLastUpdated(
        self, stations: str, states: list) -> pd.DataFrame:
        """
        Purpose:
        Adds the date a station was last updated (from states)

        Pseudocode:
        - Create the column in the DataFrame (defaults as None)
        - For each state, [add the last_updated date based on the station_id](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)

        Remarks: stations and states are both parallel
        """
        stations["last_updated"] = None

        for state in states:
            stations.loc[
                stations["station_id"] == state["station_id"], "last_updated"
            ] = state["last_updated"]

        return stations

    def findLatestDate(self, listOfDates: list) -> typing.Optional[np.datetime64]:
        """
        Purpose:
        Finds the latest date from a list of dates (datetime64)
        
        Pseudocode:
        - If the list does not contain a single value, exit
        - For each date, check if its valid
        - If there are dates, get the maximum
        - Otherwise exit
        """
        validDates = []  # Holds the list of valid dates
        latestDate = None  # The latest date, defaults to None if none are provided

        if len(listOfDates) < 1:
            return None

        for date in listOfDates:
            # Numpy evaluates each date (casting is necessairy even if casted previously)
            if not np.isnat(np.datetime64(date)):
                validDates.append(date)

        if validDates:
            latestDate = max(validDates)
        else:
            return None

        return np.datetime64(latestDate)

    def calcDateRange(
        self,
        firstYearWithData: int,
        lastUpdated: np.datetime64,
        lastYearWithData: int,
        currentYear: int = datetime.now().year,
    ) -> typing.Tuple[int, int]:
        """
        Purpose:
        Calculates the date range needed for a station to become current with its data
        
        Psuedocode:
        - Get the year we should be pulling up to based on the current year or the last year with data
        - Get the minimum year we should start pulling from based on the first year with data
        - Confirm this is infact a valid date
        - If data has been pulled before our minimum year, change the minimum year to the year data was last pulled

        Remarks: On line 108, when calculating the max year, if either are None, are error is thrown
        """
        maxYear = min(lastYearWithData, currentYear)  
        minYear = firstYearWithData  # Whenever the station started collecting data

        # Confirms the pulled year is a valid datetime (numpy)
        if not np.isnat(np.datetime64(lastUpdated)):  
            lastUpdatedDate = pd.to_datetime(lastUpdated)

            if lastUpdatedDate.year > firstYearWithData:
                minYear = lastUpdatedDate.year

        return minYear, maxYear

    def removeOlderThan(self, df: pd.DataFrame, lastUpdated: np.datetime64):
        """
        Purpose:
        Drops old/duplicate data (as per the date of the previous update - lastUpdated)
        """
        if lastUpdated:
            df.drop(df[df.date <= lastUpdated].index, inplace=True)

    def processData(self, df: pd.DataFrame, lastUpdated: np.datetime64) -> pd.DataFrame:
        """
        Purpose:
        Prepares data to be stored into the database

        Pseudocode:
        - [Drop irrelevant columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html)
        - [Rename columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html)
        - [Cast DataFrame column data types](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)
        - Remove obsolete data (would already be in the database)
        - Impute null and incorrect values
            - [dropna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html)
            - [loc](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)
            - [where](https://numpy.org/doc/stable/reference/generated/numpy.where.html)
        """
        try:
            df.drop(
                columns=[
                    "Data Quality",
                    "Max Temp Flag",
                    "Mean Temp Flag",
                    "Min Temp Flag",
                    "Heat Deg Days Flag",
                    "Cool Deg Days Flag",
                    "Spd of Max Gust (km/h)",
                    "Total Rain Flag",
                    "Total Snow Flag",
                    "Total Precip Flag",
                    "Snow on Grnd Flag",
                    "Dir of Max Gust Flag",
                    "Spd of Max Gust Flag",
                    "Heat Deg Days (°C)",
                    "Cool Deg Days (°C)",
                    "Longitude (x)",
                    "Station Name",
                    "Latitude (y)",
                    "Dir of Max Gust (10s deg)",
                ],
                inplace=True,
            )
        except:
            df.to_csv(
                "data/failed/" + str(df.iloc[0, 0]) + "_unexpected_column_names.csv",
                index=False,
            )

        df.rename(columns={df.columns[0]: "station_id"}, inplace=True)
        df.rename(columns={df.columns[1]: "date"}, inplace=True)  # (YEAR-MO-DA)
        df.rename(columns={df.columns[2]: "year"}, inplace=True)
        df.rename(columns={df.columns[3]: "month"}, inplace=True)
        df.rename(columns={df.columns[4]: "day"}, inplace=True)
        df.rename(columns={df.columns[5]: "max_temp"}, inplace=True)  # (°C)
        df.rename(columns={df.columns[6]: "min_temp"}, inplace=True)  # (°C)
        df.rename(columns={df.columns[7]: "mean_temp"}, inplace=True)  # (°C)
        df.rename(columns={df.columns[8]: "total_rain"}, inplace=True)  # (mm)
        df.rename(columns={df.columns[9]: "total_snow"}, inplace=True)  # (cm)
        df.rename(columns={df.columns[10]: "total_precip"}, inplace=True)  # (mm)
        df.rename(columns={df.columns[11]: "snow_on_grnd"}, inplace=True)  # (cm)

        df[["station_id"]] = df[["station_id"]].astype(str)
        df[["date"]] = df[["date"]].astype("datetime64[ns]")
        df[["year", "month", "day"]] = df[["year", "month", "day"]].astype(int)
        df[
            [
                "max_temp",
                "min_temp",
                "mean_temp",
                "total_rain",
                "total_snow",
                "total_precip",
                "snow_on_grnd",
            ]
        ] = df[
            [
                "max_temp",
                "min_temp",
                "mean_temp",
                "total_rain",
                "total_snow",
                "total_precip",
                "snow_on_grnd",
            ]
        ].astype(
            float
        )

        self.removeOlderThan(df, lastUpdated)

        df.dropna(subset=["mean_temp"], inplace=True)
        df.loc[df["snow_on_grnd"].isnull(), "snow_on_grnd"] = 0
        df.loc[df["total_rain"].isnull(), "total_rain"] = 0
        df.loc[df["total_snow"].isnull(), "total_snow"] = 0
        df.loc[df["total_precip"].isnull(), "total_precip"] = 0

        df["max_temp"] = np.where(
            df["max_temp"].isnull(), df["mean_temp"], df["max_temp"]
        )
        df["min_temp"] = np.where(
            df["min_temp"].isnull(), df["mean_temp"], df["min_temp"]
        )

        return df

    def dataProcessHourly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Purpose:
        Prepares data to be stored into the database

        Pseudocode:
        - [Drop irrelevant columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html)
        - [Rename columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html)
        - [Impute null and incorrect values](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)
        - [Cast DataFrame column data types](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)
        """
        df.drop(
            columns=[
                "x",
                "y",
                "ID",
                "STATION_NAME",
                "PROVINCE_CODE",
                "TEMP_FLAG",
                "DEW_POINT_TEMP_FLAG",
                "RELATIVE_HUMIDITY_FLAG",
                "PRECIP_AMOUNT_FLAG",
                "WIND_DIRECTION",
                "WIND_DIRECTION_FLAG",
                "WIND_SPEED",
                "WIND_SPEED_FLAG",
                "VISIBILITY_FLAG",
                "STATION_PRESSURE_FLAG",
                "HUMIDEX_FLAG",
                "WINDCHILL",
                "WINDCHILL_FLAG",
            ],
            inplace=True,
        )

        df.rename(columns={df.columns[0]: "station_id"}, inplace=True)
        df.rename(columns={df.columns[1]: "datetime"}, inplace=True)
        df.rename(columns={df.columns[2]: "year"}, inplace=True)
        df.rename(columns={df.columns[3]: "month"}, inplace=True)
        df.rename(columns={df.columns[4]: "day"}, inplace=True)
        df.rename(columns={df.columns[5]: "hour"}, inplace=True)
        df.rename(columns={df.columns[6]: "temp"}, inplace=True)
        df.rename(columns={df.columns[7]: "dew_point_temp"}, inplace=True)
        df.rename(columns={df.columns[8]: "humidex"}, inplace=True)
        df.rename(columns={df.columns[9]: "precip_amount"}, inplace=True)
        df.rename(columns={df.columns[10]: "rel_humid"}, inplace=True)
        df.rename(columns={df.columns[11]: "stn_press"}, inplace=True)
        df.rename(columns={df.columns[12]: "visibility"}, inplace=True)

        df.loc[df["dew_point_temp"].isnull(), "dew_point_temp"] = 0
        df.loc[df["rel_humid"].isnull(), "rel_humid"] = 0
        df.loc[df["precip_amount"].isnull(), "precip_amount"] = 0
        df.loc[df["visibility"].isnull(), "visibility"] = 0
        df.loc[df["stn_press"].isnull(), "stn_press"] = 0
        df.loc[df["humidex"].isnull(), "humidex"] = 0

        df[["station_id"]] = df[["station_id"]].astype(str)
        df[["datetime"]] = df[["datetime"]].astype("datetime64[ns]")
        df[["year", "month", "day", "hour"]] = df[
            ["year", "month", "day", "hour"]
        ].astype(int)

        df[
            [
                "dew_point_temp",
                "rel_humid",
                "precip_amount",
                "visibility",
                "stn_press",
                "humidex",
            ]
        ] = df[
            [
                "dew_point_temp",
                "rel_humid",
                "precip_amount",
                "visibility",
                "stn_press",
                "humidex",
            ]
        ].astype(
            float
        )

        return df

    def tranformHourlyToDaily(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Purpose:
        Aggregates hourly data to compress values into a single day (minimum, mean and maximum values)
        
        Psuedocode:
        - [Aggregate the data](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) [by station_id, year, month and day](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
        - [Rename the columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html)
        - [Cast DataFrame column data types](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)
        """
        # get min max mean for each day
        transformed = (
            df.groupby(["station_id", "year", "month", "day"])
            .agg(
                {
                    "temp": ["min", "max", "mean"],
                    "dew_point_temp": ["min", "max", "mean"],
                    "humidex": ["min", "max", "mean"],
                    "precip_amount": ["sum"],
                    "rel_humid": ["min", "max", "mean"],
                    "stn_press": ["min", "max", "mean"],
                    "visibility": ["min", "max", "mean"],
                }
            )
            .reset_index()
        )

        # rename columns
        transformed.columns = [  # type: ignore
            "station_id",
            "year",
            "month",
            "day",
            "min_temp",
            "max_temp",
            "mean_temp",
            "min_dew_point_temp",
            "max_dew_point_temp",
            "mean_dew_point_temp",
            "min_humidex",
            "max_humidex",
            "mean_humidex",
            "total_precip",
            "min_rel_humid",
            "max_rel_humid",
            "mean_rel_humid",
            "min_stn_press",
            "max_stn_press",
            "mean_stn_press",
            "min_visibility",
            "max_visibility",
            "mean_visibility",
        ]
        # print(transformed.columns)

        # astype float
        transformed[
            [
                "min_temp",
                "max_temp",
                "mean_temp",
                "min_dew_point_temp",
                "max_dew_point_temp",
                "mean_dew_point_temp",
                "min_humidex",
                "max_humidex",
                "mean_humidex",
                "total_precip",
                "min_rel_humid",
                "max_rel_humid",
                "mean_rel_humid",
                "min_stn_press",
                "max_stn_press",
                "mean_stn_press",
                "min_visibility",
                "max_visibility",
                "mean_visibility",
            ]
        ] = transformed[
            [
                "min_temp",
                "max_temp",
                "mean_temp",
                "min_dew_point_temp",
                "max_dew_point_temp",
                "mean_dew_point_temp",
                "min_humidex",
                "max_humidex",
                "mean_humidex",
                "total_precip",
                "min_rel_humid",
                "max_rel_humid",
                "mean_rel_humid",
                "min_stn_press",
                "max_stn_press",
                "mean_stn_press",
                "min_visibility",
                "max_visibility",
                "mean_visibility",
            ]
        ].astype(
            float
        )

        return transformed
