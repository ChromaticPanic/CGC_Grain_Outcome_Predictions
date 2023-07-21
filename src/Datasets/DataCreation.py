# -------------------------------------------
# DataCreation.py
#
# After loading the dataset, this class creates different datasets to be used in the modeling process
#
# Datasets present:
# - v1: Given a district and its weather attributes -> predict if the district is gonna have ergot or not
# - v2: Given a district and other attributes from weather, soil_moisture, soil data -> predict if the district is gonna have ergot or not
# - v3: Given an ergot sample and its all given attributes -> predict if the district is gonna have ergot or not
# - v4: Given a district and its all given attributes -> predict that if the district produced the crop which are sellable
# -------------------------------------------
from Shared.DataService import DataService
from dotenv import load_dotenv
import sqlalchemy as sq  # type: ignore
from sqlalchemy import Connection  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import os
import sys

from typing import Any, Optional

sys.path.append("../")
from Shared.DataService import DataService

LOG_FILE = "/data/pull_moisture.log"


# Load the database connection environment variables located in the docker folder
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

load_dotenv("../docker/.env")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")


# function to update logs
def updateLog(fileName: str, message: str) -> None:
    try:
        if fileName is not None:
            with open(fileName, "a") as log:
                log.write(message + "\n")
    except Exception as e:
        print(message)


def connect_db() -> sq.engine.Connection:
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        updateLog(LOG_FILE, "Missing database credentials")
        raise ValueError("Environment variables are not set")
    else:
        # connecting to database
        db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
        conn = db.connect()

    return conn


def getErgotData(conn: sq.engine.Connection) -> pd.DataFrame:
    """
    This function used to fetch aggregated ergot data from database.

    Parameters:
        conn: connection to the database
    """
    query = sq.text("select * FROM public.agg_ergot_sample")
    ergot_df = pd.read_sql(query, conn)
    return ergot_df


def getErgotSamples(conn: sq.engine.Connection) -> pd.DataFrame:
    """
    This function used to fetch ergot sample data from database.

    Parameters:
        conn: connection to the database
    """
    query = sq.text("select * FROM public.ergot_sample")
    ergot_df = pd.read_sql(query, conn)
    return ergot_df


def getWeatherData_v1(months: Optional[typing.List[Any]]) -> pd.DataFrame:
    """
    This function used to fetch aggregated weather satation data from database.

    Parameters:
        months: list of months for which the soil moisture data is required.
    note : If months is None, then the function returns the soil moisture data for all months.
    """
    # reaading the csv file
    agg_weather = pd.read_csv("../Datasets/data/aggregatedDly.csv")
    all_col = agg_weather.columns.tolist()
    uni_col = set()
    for i in range(2, len(all_col)):
        split_attr_name = all_col[i].split("_")
        if "mean" in split_attr_name[0]:
            uni_col.add(all_col[i].split(":")[1])

    # creating a new dataframe
    new_weather_df = pd.DataFrame()
    new_weather_df["year"] = agg_weather["year"]
    new_weather_df["district"] = agg_weather["district"]
    # filter for mointly data
    if months is None:
        list_months = [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
        ]
    else:
        list_months = list(months)
    for col_name in uni_col:
        fil_month_columns = agg_weather.filter(
            regex="^(" + "|".join(list_months) + ")", axis=1
        )
        fil_col = fil_month_columns.filter(like=col_name)
        new_weather_df[col_name] = fil_col.mean(axis=1)
        agg_weather.drop(columns=fil_col.columns, inplace=True)

    return new_weather_df


def getSoilMoistureData(
    conn: sq.engine.Connection, months: Optional[typing.List[Any]]
) -> pd.DataFrame:
    """
    This function used to fetch soil moisture data from database.

    Parameters:
        conn: connection to the database
        months: list of months for which the soil moisture data is required.
    note : If months is None, then the function returns the soil moisture data for all months.
    """
    if months is None:
        query = sq.text("select * FROM public.agg_soil_moisture")
    else:
        query = sq.text(
            f"select * FROM public.agg_soil_moisture where month in {tuple(months)}"
        )
    soil_moisture_df = pd.read_sql(query, conn)
    return soil_moisture_df


def getSoilData(conn: sq.engine.Connection) -> pd.DataFrame:
    """
    This function used to fetch soil(type) data from database.

    Parameters:
        conn: connection to the database
    """
    query = sq.text("select * FROM public.agg_soil_data")
    soil_df = pd.read_sql(query, conn)
    return soil_df


def calcUIDs(ergot: pd.DataFrame) -> pd.DataFrame:
    ergot.loc[ergot["province"] == "MB", "district"] = (
        ergot.loc[ergot["province"] == "MB", "crop_district"] + 4600
    )
    ergot.loc[ergot["province"] == "SK", "district"] = (
        ergot.loc[ergot["province"] == "SK", "crop_district"] - 1
    ) + 4700
    ergot.loc[ergot["province"] == "AB", "district"] = (
        ergot.loc[ergot["province"] == "AB", "crop_district"] * 10
    ) + 4800

    ergot[["district"]] = ergot[["district"]].astype(int)

    return ergot


def getDatasetV1(months: Optional[typing.List[Any]]) -> pd.DataFrame:
    """
    v1: contains only has_ergot as an output from ergot table and all the weather attributes as input from weather table
        Target: "has_ergot" from ergot table

    Problem statement: Given a district and its weather attributes -> predict if the district is gonna have ergot or not.

    Parameters:
        months: list of months for which the soil moisture data is required.
    note : If months is None, then the function returns the soil moisture data for all months.

    To-do: we currently take the mean of all months for each attribute ->
        need to test on specific months because ergot won't grow in winter
    """
    conn = connect_db()
    ergot_df = getErgotData(conn)
    # drop district 4730 because it has no weather data
    ergot_df.drop(ergot_df[ergot_df["district"] == 4730].index, inplace=True)
    ergot_df = ergot_df[["year", "district", "has_ergot"]]

    # get weather data
    weather_df = getWeatherData_v1(months)
    conn.close()
    dataset_v1 = weather_df.merge(ergot_df, on=["year", "district"])
    return dataset_v1


def getDatasetV2(months: Optional[typing.List[Any]]) -> pd.DataFrame:
    """
    v_2: contains only has_ergot as an output from ergot table and all attributes from weather, soil_moisture, soil data as input
        Target: "has_ergot" from ergot table

    Problem statement: Given a district and other attributes from weather, soil_moisture, soil data -> predict if the district is gonna have ergot or not.

    Parameters:
        months: list of months for which the soil moisture data is required.
    note : If months is None, then the function returns the soil moisture data for all months.

    To-do: Need to get the weather data|soil_moisture for only the month with the appearance of ergot (ergot wont grow in winter)
    """
    conn = connect_db()

    # Get ergot data
    ergot_df = getErgotData(conn)
    # drop district 4730 because it has no weather data and year = 2022 since soil moisture data is only until 2021.
    ergot_df.drop(
        ergot_df[(ergot_df.year == 2022) | (ergot_df.district == 4730)].index,
        inplace=True,
    )
    ergot_df = ergot_df[["year", "district", "has_ergot"]]

    # Get soil moisture data
    soil_moisture_df = getSoilMoistureData(conn, months).drop(
        columns=[
            "index",
            "cr_num",
            "soil_moisture_min",
            "soil_moisture_max",
            "month",
            "day",
        ]
    )
    soil_moisture_df = (
        soil_moisture_df.groupby(["year", "district"]).mean().reset_index()
    )

    df = ergot_df.merge(soil_moisture_df, on=["year", "district"])

    # Get soil data
    soil_df = getSoilData(conn)
    df = df.merge(soil_df, on=["district"], how="left")

    # Get weather data
    weather_df = getWeatherData_v1(months)
    df = df.merge(weather_df, on=["year", "district"])

    return df


def getDatasetV3(months: Optional[typing.List[Any]]) -> pd.DataFrame:
    """
    v_3: contains ergot, weather, soil_moisture, soil data
        Target: "incidence" from ergot table

    Problem statement: Given an ergot sample and its all given attributes -> predict if the district is gonna have ergot or not.

    Parameters:
        months: list of months for which the soil moisture data is required.
    note : If months is None, then the function returns the soil moisture data for all months.

    To-do: we currently take the mean of all months for each attribute ->
        need to test on specific months because ergot won't grow in winter
    """

    conn = connect_db()

    # Get ergot data
    ergot_df = calcUIDs(getErgotSamples(conn))
    ergot_df.drop(columns=["sample_id", "crop_district", "province"], inplace=True)
    ergot_df.drop(
        ergot_df[(ergot_df["year"] == 2022) | (ergot_df.district == 4730)].index,
        inplace=True,
    )

    sm_df = getSoilMoistureData(conn, months).drop(
        columns=[
            "index",
            "cr_num",
            "soil_moisture_min",
            "soil_moisture_max",
            "month",
            "day",
        ]
    )

    # Get soil moisture data
    sm_df = sm_df.groupby(["year", "district"]).mean().reset_index()

    df = ergot_df.merge(sm_df, on=["year", "district"], how="left")

    # Get soil data
    soil_df = getSoilData(conn)
    df = df.merge(soil_df, on=["district"], how="left")

    # Get weather data
    weather_df = getWeatherData_v1(months)
    weather_df.drop(weather_df[weather_df["year"] == 2022].index, inplace=True)
    df = df.merge(weather_df, on=["year", "district"])

    return df


def getDatasetV4(months: Optional[typing.List[Any]]) -> pd.DataFrame:
    """
    v_4: contains ergot, weather, soil_moisture, soil data
        Target: "sellable" from ergot table

    Problem statement: Given a district and its all given attributes -> predict that if the district produced the crop which are sellable.

    Parameters:
        months: list of months for which the soil moisture data is required.
    note : If months is None, then the function returns the soil moisture data for all months.

    To-do: we currently take the mean of all months for each attribute ->
        need to test on specific months because ergot won't grow in winter
    """

    conn = connect_db()

    # Get ergot data
    agg_ergot_df = getErgotData(conn)
    # drop district 4730 because it has no weather data and year = 2022 since soil moisture data is only until 2021.
    agg_ergot_df.drop(
        agg_ergot_df[
            (agg_ergot_df.year == 2022) | (agg_ergot_df.district == 4730)
        ].index,
        inplace=True,
    )

    # Get ergot data
    ergot_df = calcUIDs(getErgotSamples(conn))
    ergot_df.drop(columns=["sample_id", "crop_district", "province"], inplace=True)
    ergot_df.drop(
        ergot_df[(ergot_df["year"] == 2022) | (ergot_df.district == 4730)].index,
        inplace=True,
    )

    ergot_df["sellable"] = np.where(
        ergot_df["severity"] > 0.04, False, True
    )  # new column for sellable crop or not
    ergot_df.drop(columns=["severity", "incidence"], inplace=True)

    # merging both ergot tables
    new_ergot_df = pd.merge(agg_ergot_df, ergot_df, on=["year", "district"])

    sm_df = getSoilMoistureData(conn, months).drop(
        columns=[
            "index",
            "cr_num",
            "soil_moisture_min",
            "soil_moisture_max",
            "month",
            "day",
        ]
    )

    # Get soil moisture data
    sm_df = sm_df.groupby(["year", "district"]).mean().reset_index()

    df = sm_df.merge(new_ergot_df, on=["year", "district"], how="left")

    # Get soil data
    soil_df = getSoilData(conn)
    df = df.merge(soil_df, on=["district"], how="left")

    # Get weather data
    weather_df = getWeatherData_v1(months)
    weather_df.drop(weather_df[weather_df["year"] == 2022].index, inplace=True)
    df = df.merge(weather_df, on=["year", "district"])

    return df
