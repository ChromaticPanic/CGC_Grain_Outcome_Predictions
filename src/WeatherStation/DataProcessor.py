# ----------------------------------------------------
# DataProcessor.py
#
# Purpose: handles the more complex data processing and manipulations for ScrapeStations.py
# ----------------------------------------------------
from datetime import datetime
import numpy as np
import pandas as pd
import typing


class DataProcessor:
    @typing.no_type_check  # need to define a data class for this
    def removeInactive(
        self, stations: pd.DataFrame, states: list({str, np.datetime64, bool})
    ) -> pd.DataFrame:
        for state in states:
            if not state["is_active"]:
                stations.drop(
                    stations[stations.station_id == state["station_id"]].index,
                    inplace=True,
                )

        return stations

    @typing.no_type_check  # need to define a data class for this
    def addLastUpdated(
        self, stations: str, states: list({str, np.datetime64, bool})
    ) -> pd.DataFrame:
        stations["last_updated"] = None

        for state in states:
            stations.loc[
                stations["station_id"] == state["station_id"], "last_updated"
            ] = state["last_updated"]

        return stations

    def findLatestDate(self, listOfDates: list) -> np.datetime64 | None:
        validDates = []  # Holds the list of valid dates
        latestDate = (
            None  # Holds the latest date, defaults to None if no valid dates are given
        )

        if len(listOfDates) < 1:
            return None

        for date in listOfDates:
            if not np.isnat(
                np.datetime64(date)
            ):  # Numpy evaluates each date (casting is necessairy even if casted previously)
                validDates.append(date)

        if validDates:
            latestDate = max(validDates)

        return np.datetime64(latestDate)

    def calcDateRange(
        self,
        firstYearWithData: int,
        lastUpdated: np.datetime64,
        lastYearWithData: int,
        currentYear: int = datetime.now().year,
    ) -> typing.Tuple[int, int]:
        maxYear = min(
            lastYearWithData, currentYear
        )  # Pull to the current year or whatever year the data goes up until (if either are None throws error)
        minYear = firstYearWithData  # Whenever the station started collecting data

        if not np.isnat(
            np.datetime64(lastUpdated)
        ):  # Confirms the pulled year is a valid datetime (numpy)
            lastUpdatedDate = pd.to_datetime(lastUpdated)

            if lastUpdatedDate.year > firstYearWithData:
                minYear = lastUpdatedDate.year

        return minYear, maxYear

    def removeOlderThan(self, df: pd.DataFrame, lastUpdated: np.datetime64):
        if lastUpdated:
            df.drop(
                df[df.date <= lastUpdated].index, inplace=True
            )  # Drops old/duplicate data (as per the date of the previous update - lastUpdated)

    def processData(self, df: pd.DataFrame, lastUpdated: np.datetime64) -> pd.DataFrame:
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
        # print(transformed.columns)

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
