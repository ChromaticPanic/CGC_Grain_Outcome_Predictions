from dotenv import load_dotenv
import sqlalchemy as sq  # type: ignore
import pandas as pd  # type: ignore
import os, sys

sys.path.append("../")
from Shared.DataService import DataService

LOG_FILE = "/data/pull_moisture.log"
load_dotenv()
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


def connect_db() -> sq.Connection:
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


def getErgotData(conn: sq.Connection) -> pd.DataFrame:
    query = sq.text("select * FROM public.agg_ergot_samples")
    ergot_df = pd.read_sql(query, conn)
    return ergot_df


def getWeatherData_v1() -> pd.DataFrame:
    agg_weather = pd.read_csv("Datasets/aggregatedDly.csv")
    all_col = agg_weather.columns.tolist()
    uni_col = set()
    for i in range(2, len(all_col)):
        split_attr_name = all_col[i].split("_")
        if "mean" in split_attr_name[0]:
            uni_col.add(all_col[i].split(":")[1])

    new_weather_df = pd.DataFrame()
    new_weather_df["year"] = agg_weather["year"]
    new_weather_df["district"] = agg_weather["district"]
    for col_name in uni_col:
        fil_col = agg_weather.filter(like=col_name)
        new_weather_df[col_name] = fil_col.mean(axis=1)
        agg_weather.drop(columns=fil_col.columns, inplace=True)

    return new_weather_df


def getSoilMoistureData(conn: sq.Connection, months: list | None) -> pd.DataFrame:
    """
    This function is called with 2 parameters conn and months.
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


def getSoilData(conn: sq.Connection) -> pd.DataFrame:
    query = sq.text("select * FROM public.agg_soil_data")
    soil_df = pd.read_sql(query, conn)
    return soil_df


def getDatasetV1() -> pd.DataFrame:
    """
    v1: contains only has_ergot as an output from ergot table and all the weather attributes as input from weather table
    This dataset is used for the following stated problem:
        Given a district and its weather attributes -> predict if the district is gonna have ergot or not.
    To-do: we currently take the mean of all months for each attribute ->
        need to test on specific months because ergot won't grow in winter
    """
    conn = connect_db()
    ergot_df = getErgotData(conn)
    # drop district 4730 because it has no weather data
    ergot_df.drop(ergot_df[ergot_df["district"] == 4730].index, inplace=True)
    ergot_df = ergot_df[["year", "district", "has_ergot"]]

    # get weather data
    weather_df = getWeatherData_v1()
    conn.close()
    dataset_v1 = weather_df.merge(ergot_df, on=["year", "district"])
    return dataset_v1


def getDatasetV2() -> pd.DataFrame:
    """
    v_2: contains ergot, weather, soil_moisture, soil data
    Same problem statement as v1
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
    soil_moisture_df = getSoilMoistureData(conn, None).drop(
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
    weather_df = getWeatherData_v1()
    df = df.merge(weather_df, on=["year", "district"])

    return df
