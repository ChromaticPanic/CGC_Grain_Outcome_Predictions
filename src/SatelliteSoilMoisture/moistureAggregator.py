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


load_dotenv()
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")


class MoistureAggregator:
    def __init__(self):
        if (
            PG_DB is None
            or PG_ADDR is None
            or PG_PORT is None
            or PG_USER is None
            or PG_PW is None
        ):
            raise ValueError("Environment variables are not set")

        # connicting to database
        db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
        conn = db.connect()

        self.moistureData = self.__pullMoistureData(conn)
        self.helper = AggregatorHelper()

        db.cleanup()

        # extracts day, month, year, week from the date then deletes the date altogether
        self.moistureData["date"] = pd.to_datetime(self.moistureData["date"])
        self.moistureData["day"] = self.moistureData["date"].dt.day
        self.moistureData["month"] = self.moistureData["date"].dt.month
        self.moistureData["year"] = self.moistureData["date"].dt.year

        self.moistureData.drop(columns="date", inplace=True)

        # setup for weekly aggregations
        self.moistureData["week"] = None
        dates = self.helper.getDatesInYr()

        for date in dates:
            dateComponents = date.split("-")
            monthInt = int(dateComponents[0])
            dayInt = int(dateComponents[1])
            weekInt = datetime.date(2001, monthInt, dayInt).isocalendar()[1]

            self.moistureData.loc[
                (self.moistureData["month"] == monthInt)
                & (self.moistureData["day"] == dayInt),
                "week",
            ] = weekInt

    def aggregateByDay(self, pathToSave):
        agg_df = (
            self.moistureData.groupby(["district", "year", "month", "day"])
            .agg({"soil_moisture": ["min", "max", "mean"]})
            .reset_index()
        )

        # sets the column names for the aggregate dataframe
        agg_df.columns = [  # type: ignore
            "district",
            "year",
            "month",
            "day",
            "soil_moisture_min",
            "soil_moisture_max",
            "soil_moisture_mean"
        ]

        dates = self.helper.getDatesInYr()
        final_df = self.helper.reshapeDataByDates(
            dates, agg_df, self.moistureData, "dates"
        )

        try:
            final_df.to_csv(
                path_or_buf=f"{pathToSave}/agg_moisture_by_day.csv",
                sep=",",
                columns=final_df.columns.tolist(),
            )
        except Exception as e:
            print("[ERROR]")
            print(e)

    def aggregateByWeek(self, pathToSave):
        agg_df = (
            self.moistureData.groupby(["district", "year", "week"])
            .agg({"soil_moisture": ["min", "max", "mean"]})
            .reset_index()
        )

        # sets the column names for the aggregate dataframe
        agg_df.columns = [  # type: ignore
            "district",
            "year",
            "week",
            "soil_moisture_min",
            "soil_moisture_max",
            "soil_moisture_mean"
        ]

        dates = self.helper.getWeeksInYr()
        final_df = self.helper.reshapeDataByDates(
            dates, agg_df, self.moistureData, "weeks"
        )

        try:
            final_df.to_csv(
                path_or_buf=f"{pathToSave}/agg_moisture_by_week.csv",
                sep=",",
                columns=final_df.columns.tolist(),
            )
        except Exception as e:
            print("[ERROR]")
            print(e)

    def aggregateByMonth(self, pathToSave):

        agg_df = (
            self.moistureData.groupby(["district", "year", "month"])
            .agg({"soil_moisture": ["min", "max", "mean"]})
            .reset_index()
        )

        # sets the column names for the aggregate dataframe
        agg_df.columns = [  # type: ignore
            "district",
            "year",
            "month",
            "soil_moisture_min",
            "soil_moisture_max",
            "soil_moisture_mean"
        ]

        dates = self.helper.getMonthsInYr()
        final_df = self.helper.reshapeDataByDates(
            dates, agg_df, self.moistureData, "months"
        )

        try:
            final_df.to_csv(
                path_or_buf=f"{pathToSave}/agg_moisture_by_month.csv",
                sep=",",
                columns=final_df.columns.tolist(),
            )
        except Exception as e:
            print("[ERROR]")
            print(e)

    def __pullMoistureData(self, conn):
        moistureQuery = sq.text(
            """
            SELECT * FROM public.soil_moisture
            WHERE district IS NOT NULL;
            """
        )

        return pd.read_sql(moistureQuery, conn)
