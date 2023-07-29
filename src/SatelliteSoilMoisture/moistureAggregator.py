# -------------------------------------------
# moistureAggregator.py
#
# After loading the soil moisture data the following class can be used to calculate the minimum, mean and maximum of all attributes per district
#   soil_moisture: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#soil_moisture
#
# Output:
#   An excel document with the expected output columns (saves as specified by pathToSave i.e datasets uses datasets/data/)
#
# Remarks:
#  - This class is used by the setCreator
#  - As weeks change per year, the weekly aggregation uses the year of 2001 (not a leap year)
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


SOIL_MOISTURE_TABLE = "soil_moisture"  # table that contains the soil moisture data


try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# Load the database connection environment variables located in the docker folder
load_dotenv("../docker/.env")
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
        db.cleanup()

        self.helper = AggregatorHelper()

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

            #  calculate the week number (52 weeks in a year)
            weekInt = datetime.date(2001, monthInt, dayInt).isocalendar()[1]

            #  Assign week numbers (week) based on the month and day in the DataFrame
            self.moistureData.loc[
                (self.moistureData["month"] == monthInt)
                & (self.moistureData["day"] == dayInt),
                "week",
            ] = weekInt

    def aggregateByDay(self, pathToSave):
        """
        Purpose:
        Aggregate the soil moisture data by district, year, month and day

        Psuedocode:
        - Aggregate the columns by district, year, monthy, day
        - Name the columns into the final DataFrame
        - Get the unique dates in a year formatted as MO-DA
        - Reshape the rows to transform them into columns where each attribute reappears for each date
        - Export to csv
        """
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
            "soil_moisture_mean",
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
        """
        Purpose:
        Aggregate the soil moisture data by district, year and week

        Psuedocode:
        - Aggregate the columns by district, year and week
        - Name the columns into the final DataFrame
        - Get the unique dates in a year formatted as W
        - Reshape the rows to transform them into columns where each attribute reappears for each date
        - Export to csv
        """
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
            "soil_moisture_mean",
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
        """
        Purpose:
        Aggregate the soil moisture data by district, year and month

        Psuedocode:
        - Aggregate the columns by district, year and month
        - Name the columns into the final DataFrame
        - Get the unique dates in a year formatted as M:
        - Reshape the rows to transform them into columns where each attribute reappears for each date
        - Export to csv
        """
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
            "soil_moisture_mean",
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
        """
        Purpose:
        Loads the soil moisture data from the soil moisture table

        Tables:
        - [soil_moisture](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#soil_moisture)

        Psuedocode:
        - Create the weather station data SQL query
        - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
        """
        moistureQuery = sq.text(
            f"""
            SELECT * FROM public.{SOIL_MOISTURE_TABLE}
            WHERE district IS NOT NULL;
            """
        )

        return pd.read_sql(moistureQuery, conn)
