import sqlalchemy as sq  # type: ignore
import pandas as pd  # type: ignore
from dotenv import load_dotenv
import os, sys, datetime

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService
from Shared.aggregatorHelper import AggregatorHelper


load_dotenv()
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

        # merge both the weather station data and the station data together
        self.df = self.weatherData.merge(self.stationData, on="station_id")
        self.helper = AggregatorHelper()

        db.cleanup()

        # setup for weekly aggregations
        self.df["week"] = None
        dates = self.helper.getDatesInYr()

        for date in dates:
            dateComponents = date.split("-")
            monthInt = int(dateComponents[0])
            dayInt = int(dateComponents[1])
            weekInt = datetime.date(2001, monthInt, dayInt).isocalendar()[1]

            self.df.loc[
                (self.df["month"] == monthInt) & (self.df["day"] == dayInt), "week"
            ] = weekInt

    def aggregateByDay(self, pathToSave):
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
        # pulling weather station data from the database
        weatherDataQuery = sq.text(
            """
            SELECT * FROM public.ab_hly_station_data
            UNION
            SELECT * FROM public.mb_hly_station_data
            UNION
            SELECT * FROM public.sk_hly_station_data;
            """
        )

        return pd.read_sql(weatherDataQuery, conn)

    def __pullStationData(self, conn: sq.engine.Connection) -> pd.DataFrame:
        # pulling station data from the database
        stationDataQuery = sq.text(
            """
            SELECT station_id, district FROM public.stations_dly
            WHERE district IS NOT NULL;
            """
        )

        stationData = pd.read_sql(stationDataQuery, conn)
        stationData[["district"]] = stationData[["district"]].astype(int)

        return stationData
