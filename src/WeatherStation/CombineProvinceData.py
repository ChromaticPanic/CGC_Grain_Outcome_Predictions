# %%
import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os, sys, calendar

sys.path.append("../")
from Shared.DataService import DataService

# %%
load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")

if (
    PG_DB is None
    or PG_ADDR is None
    or PG_PORT is None
    or PG_USER is None
    or PG_PW is None
):
    raise ValueError("Environment variables not set")


# %%
def pullHlyWeatherData(conn: sq.engine.Connection) -> pd.DataFrame:
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


# %%
def pullDlyWeatherData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.ab_dly_station_data
        UNION
        SELECT * FROM public.mb_dly_station_data
        UNION
        SELECT * FROM public.sk_dly_station_data;
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def aggregateHlyData(df: pd.DataFrame) -> pd.DataFrame:
    # aggregate the values in the dataframe by date and district
    agg_df = (
        df.groupby(["district", "year", "month", "day"])
        .agg(
            {
                "min_temp": "min",
                "max_temp": "max",
                "mean_temp": "mean",
                "min_dew_point_temp": "min",
                "max_dew_point_temp": "max",
                "mean_dew_point_temp": "mean",
                "min_humidex": "min",
                "max_humidex": "max",
                "mean_humidex": "mean",
                "total_precip": ["min", "max", "mean"],
                "min_rel_humid": "min",
                "max_rel_humid": "max",
                "mean_rel_humid": "mean",
                "min_stn_press": "min",
                "max_stn_press": "max",
                "mean_stn_press": "mean",
                "min_visibility": "min",
                "max_visibility": "max",
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

    return agg_df


# %%
def aggregateDlyData(df: pd.DataFrame) -> pd.DataFrame:
    # aggregate the values in the dataframe by date and district
    agg_df = (
        df.groupby(["district", "year", "month", "day"])
        .agg(
            {
                "max_temp": "max",
                "min_temp": "min",
                "mean_temp": "mean",
                "total_rain": ["min", "max", "mean"],
                "total_snow": ["min", "max", "mean"],
                "total_precip": ["min", "max", "mean"],
                "snow_on_grnd": ["min", "max", "mean"],
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
        "max_temp",
        "min_temp",
        "mean_temp",
        "min_total_rain",
        "max_total_rain",
        "mean_total_rain",
        "min_total_snow",
        "max_total_snow",
        "mean_total_snow",
        "min_total_precip",
        "max_total_precip",
        "mean_total_precip",
        "min_snow_on_grnd",
        "max_snow_on_grnd",
        "mean_snow_on_grnd",
    ]

    return agg_df


# %%
def pullStationData(conn: sq.engine.Connection) -> pd.DataFrame:
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


# %%
def main():
    TABLENAME = "agg_weather_combined"

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    conn = db.connect()

    weatherDataHly = pullHlyWeatherData(conn)
    weatherDataDly = pullDlyWeatherData(conn)
    stationData = pullStationData(conn)

    # merge both the weather station data and the station data together
    dfHly = weatherDataHly.merge(stationData, on="station_id")
    dfDly = weatherDataDly.merge(stationData, on="station_id")

    # drop station_id column
    dfHly = dfHly.drop(columns=["station_id"])
    dfDly = dfDly.drop(columns=["station_id"])

    agg_dfHly = aggregateHlyData(dfHly)
    agg_dfDly = aggregateDlyData(dfDly)

    # merge on year month day district
    dfCombined = agg_dfHly.merge(agg_dfDly, on=["year", "month", "day", "district"])

    try:
        dfCombined.to_sql(
            TABLENAME, conn, schema="public", if_exists="append", index=False
        )
    except Exception as e:
        print("An error occurred while writing to the database {}".format(e))
        raise e

    db.cleanup()


# %%
if __name__ == "__main__":
    main()
