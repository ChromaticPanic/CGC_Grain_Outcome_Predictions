# -------------------------------------------
# hlyAggregator.py
#
# After loading the hourly weather station data the following class can be used to calculate the minimum, mean and maximum of all attributes per district
#   stations_hly: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_hly
#   ab_hly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_hly_station_data
#   mb_hly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_hly_station_data
#   sk_hly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_hly_station_data
#
# Output:
#   An excel document with the expected output columns (saves as specified by pathToSave i.e datasets uses datasets/data/)
#
# Remarks: As weeks change per year, the weekly aggregation uses the year of 2001 (not a leap year)
# -------------------------------------------
from dotenv import load_dotenv
import sqlalchemy as sq
import pandas as pd
import os, sys, datetime

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService
from Shared.aggregatorHelper import AggregatorHelper  # type: ignore


HLY_STATIONS = "stations_hly"  # table that contains the hourly stations

AB_HLY_TABLE = "ab_hly_station_data"  # table that contains Albertas data
MB_HLY_TABLE = "mb_hly_station_data"  # table that contains Manitobas data
SK_HLY_TABLE = "sk_hly_station_data"  # table that contains Saskatchewans data


# Load the database connection environment variables located in the docker folder
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

load_dotenv("../docker/.env")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


class HlyAggregator:
    def __init__(self):
        if (
            PG_DB is None
            or PG_ADDR is None
            or PG_PORT is None
            or PG_USER is None
            or PG_PW is None
        ):
            raise ValueError("Environment variables not set")

        db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
        conn = db.connect()

        self.weatherData = self.__pullWeatherData(conn)
        self.stationData = self.__pullStationData(conn)
        db.cleanup()

        # merge both the weather station data and the station data together
        self.df = self.weatherData.merge(self.stationData, on="station_id")
        self.helper = AggregatorHelper()

        # setup for weekly aggregations by calculating the week number for all dates
        self.df["week"] = None
        dates = self.helper.getDatesInYr()

        for date in dates:
            dateComponents = date.split("-")
            monthInt = int(dateComponents[0])
            dayInt = int(dateComponents[1])

            #  calculate the week number (52 weeks in a year)
            weekInt = datetime.date(2001, monthInt, dayInt).isocalendar()[1]

            #  Assign week numbers (week) based on the month and day in the DataFrame
            self.df.loc[
                (self.df["month"] == monthInt) & (self.df["day"] == dayInt), "week"
            ] = weekInt

    def aggregateByDay(self, pathToSave):
        """
        Purpose:
        Aggregate the hourly weather station data by district, year, month and day

        Psuedocode:
        - Aggregate the columns by district, year, monthy, day
        - Name the columns into the final DataFrame
        - Get the unique dates in a year formatted as MO-DA
        - Reshape the rows to transform them into columns where each attribute reappears for each date
        - Export to csv
        """
        agg_df = (
            self.df.groupby(["district", "year", "month", "day"])
            .agg(
                {
                    "min_temp": "mean",
                    "max_temp": "mean",
                    "mean_temp": "mean",
                    "min_dew_point_temp": "mean",
                    "max_dew_point_temp": "mean",
                    "mean_dew_point_temp": "mean",
                    "min_humidex": "mean",
                    "max_humidex": "mean",
                    "mean_humidex": "mean",
                    "total_precip": ["min", "max", "mean"],
                    "min_rel_humid": "mean",
                    "max_rel_humid": "mean",
                    "mean_rel_humid": "mean",
                    "min_stn_press": "mean",
                    "max_stn_press": "mean",
                    "mean_stn_press": "mean",
                    "min_visibility": "mean",
                    "max_visibility": "mean",
                    "mean_visibility": "mean",
                }
            )
            .reset_index()
        )

        # sets the column names for the aggregate dataframe
        agg_df.columns = [  # type: ignore
            "district",
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
            "min_precip",
            "max_precip",
            "mean_precip",
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

        dates = self.helper.getDatesInYr()
        final_df = self.helper.reshapeDataByDates(
            dates, agg_df, self.stationData, "dates"
        )

        try:
            final_df.to_csv(
                path_or_buf=f"{pathToSave}/agg_hly_by_day.csv",
                sep=",",
                columns=final_df.columns.tolist(),
            )
        except Exception as e:
            print("[ERROR]")
            print(e)

    def aggregateByWeek(self, pathToSave):
        """
        Purpose:
        Aggregate the hourly weather station data by district, year and week

        Psuedocode:
        - Aggregate the columns by district, year and week
        - Name the columns into the final DataFrame
        - Get the unique dates in a year formatted as W
        - Reshape the rows to transform them into columns where each attribute reappears for each date
        - Export to csv
        """
        agg_df = (
            self.df.groupby(["district", "year", "week"])
            .agg(
                {
                    "min_temp": "mean",
                    "max_temp": "mean",
                    "mean_temp": "mean",
                    "min_dew_point_temp": "mean",
                    "max_dew_point_temp": "mean",
                    "mean_dew_point_temp": "mean",
                    "min_humidex": "mean",
                    "max_humidex": "mean",
                    "mean_humidex": "mean",
                    "total_precip": ["min", "max", "mean"],
                    "min_rel_humid": "mean",
                    "max_rel_humid": "mean",
                    "mean_rel_humid": "mean",
                    "min_stn_press": "mean",
                    "max_stn_press": "mean",
                    "mean_stn_press": "mean",
                    "min_visibility": "mean",
                    "max_visibility": "mean",
                    "mean_visibility": "mean",
                }
            )
            .reset_index()
        )

        # sets the column names for the aggregate dataframe
        agg_df.columns = [  # type: ignore
            "district",
            "year",
            "week",
            "min_temp",
            "max_temp",
            "mean_temp",
            "min_dew_point_temp",
            "max_dew_point_temp",
            "mean_dew_point_temp",
            "min_humidex",
            "max_humidex",
            "mean_humidex",
            "min_precip",
            "max_precip",
            "mean_precip",
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

        dates = self.helper.getWeeksInYr()
        final_df = self.helper.reshapeDataByDates(
            dates, agg_df, self.stationData, "weeks"
        )

        try:
            final_df.to_csv(
                path_or_buf=f"{pathToSave}/agg_hly_by_week.csv",
                sep=",",
                columns=final_df.columns.tolist(),
            )
        except Exception as e:
            print("[ERROR]")
            print(e)

    def aggregateByMonth(self, pathToSave):
        """
        Purpose:
        Aggregate the hourly weather station data by district, year and month

        Psuedocode:
        - Aggregate the columns by district, year and month
        - Name the columns into the final DataFrame
        - Get the unique dates in a year formatted as M:
        - Reshape the rows to transform them into columns where each attribute reappears for each date
        - Export to csv
        """
        agg_df = (
            self.df.groupby(["district", "year", "month"])
            .agg(
                {
                    "min_temp": "mean",
                    "max_temp": "mean",
                    "mean_temp": "mean",
                    "min_dew_point_temp": "mean",
                    "max_dew_point_temp": "mean",
                    "mean_dew_point_temp": "mean",
                    "min_humidex": "mean",
                    "max_humidex": "mean",
                    "mean_humidex": "mean",
                    "total_precip": ["min", "max", "mean"],
                    "min_rel_humid": "mean",
                    "max_rel_humid": "mean",
                    "mean_rel_humid": "mean",
                    "min_stn_press": "mean",
                    "max_stn_press": "mean",
                    "mean_stn_press": "mean",
                    "min_visibility": "mean",
                    "max_visibility": "mean",
                    "mean_visibility": "mean",
                }
            )
            .reset_index()
        )

        # sets the column names for the aggregate dataframe
        agg_df.columns = [  # type: ignore
            "district",
            "year",
            "month",
            "min_temp",
            "max_temp",
            "mean_temp",
            "min_dew_point_temp",
            "max_dew_point_temp",
            "mean_dew_point_temp",
            "min_humidex",
            "max_humidex",
            "mean_humidex",
            "min_precip",
            "max_precip",
            "mean_precip",
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

        dates = self.helper.getMonthsInYr()
        final_df = self.helper.reshapeDataByDates(
            dates, agg_df, self.stationData, "months"
        )

        try:
            final_df.to_csv(
                path_or_buf=f"{pathToSave}/agg_hly_by_month.csv",
                sep=",",
                columns=final_df.columns.tolist(),
            )
        except Exception as e:
            print("[ERROR]")
            print(e)

    def __pullWeatherData(self, conn: sq.engine.Connection) -> pd.DataFrame:
        """
        Purpose:
        Loads the weather station data per province from the weather station data tables

        Tables:
        - [ab_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_hly_station_data)
        - [mb_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_hly_station_data)
        - [sk_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_hly_station_data)

        Psuedocode:
        - Create the weather station data SQL query
        - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
        """
        weatherDataQuery = sq.text(
            f"""
            SELECT * FROM public.{AB_HLY_TABLE}
            UNION
            SELECT * FROM public.{MB_HLY_TABLE}
            UNION
            SELECT * FROM public.{SK_HLY_TABLE};
            """
        )

        return pd.read_sql(weatherDataQuery, conn)

    def __pullStationData(self, conn: sq.engine.Connection) -> pd.DataFrame:
        """
        Purpose:
        Loads the weather stations from the hourly weather station table

        Tables:
        - [stations_hly](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_hly)

        Psuedocode:
        - Create the weather station SQL query
        - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
        - [Cast district into an integer](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)

        Remarks: if district is not casted, future methods will throw errors
        """
        stationDataQuery = sq.text(
            f"""
            SELECT station_id, district FROM public.{HLY_STATIONS}
            WHERE district IS NOT NULL;
            """
        )

        stationData = pd.read_sql(stationDataQuery, conn)
        stationData[["district"]] = stationData[["district"]].astype(int)

        return stationData
