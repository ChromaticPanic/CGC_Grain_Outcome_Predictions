# -------------------------------------------
# combineProvinceData.py
#
# After loading the daily weather stations, hourly weather stations, daily weather station data and houly weather station data,
# the following class can be used to calculate the minimum, mean and maximum of all attributes per district
#   stations_dly: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_dly
#   stations_hly: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_hly
#   dly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_hly_station_data
#   hly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_dly_station_data
#
# Output:
#   - [agg_weather_combined](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_weather_combined)
# -------------------------------------------
from dotenv import load_dotenv
import sqlalchemy as sq
import pandas as pd
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService


DLY_STATIONS = "stations_dly"  # table that contains the hourly stations
HLY_STATIONS = "stations_hly"  # table that contains the hourly stations

AB_DLY_TABLE = "ab_dly_station_data"  # table that contains Albertas data
MB_DLY_TABLE = "mb_dly_station_data"  # table that contains Manitobas data
SK_DLY_TABLE = "sk_dly_station_data"  # table that contains Saskatchewans data

AB_HLY_TABLE = "ab_hly_station_data"  # table that contains Albertas data
MB_HLY_TABLE = "mb_hly_station_data"  # table that contains Manitobas data
SK_HLY_TABLE = "sk_hly_station_data"  # table that contains Saskatchewans data

TABLENAME = "agg_weather_combined"  # The name of the table that will hold the results


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


def main():
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

def pullHlyWeatherData(conn: sq.engine.Connection) -> pd.DataFrame:
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

def pullDlyWeatherData(conn: sq.engine.Connection) -> pd.DataFrame:
    """
    Purpose:
    Loads the weather station data per province from the weather station data tables

    Tables:
    - [ab_dly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_dly_station_data)
    - [mb_dly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_dly_station_data)
    - [sk_dly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_dly_station_data)

    Psuedocode:
    - Create the weather station data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    """
    weatherDataQuery = sq.text(
        f"""
        SELECT * FROM public.{AB_DLY_TABLE}
        UNION
        SELECT * FROM public.{MB_DLY_TABLE}
        UNION
        SELECT * FROM public.{SK_DLY_TABLE};
        """
    )

    return pd.read_sql(weatherDataQuery, conn)

def aggregateHlyData(df: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the hourly weather station data by district, year, month and day

    Psuedocode:
    - Aggregate the columns by district, year, month and day
    - Name the columns into the final DataFrame
    """
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

def aggregateDlyData(df: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the daily weather station data by district and date

    Psuedocode:
    - Aggregate the columns by district and date
    - Name the columns into the final DataFrame
    """
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

def pullStationData(conn: sq.engine.Connection) -> pd.DataFrame:
    """
    Purpose:
    Loads the weather stations from the daily weather station table

    Tables:
    - [stations_dly](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_dly)

    Psuedocode:
    - Create the weather station SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - [Cast district into an integer](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)

    Remarks: if district is not casted, future methods will throw errors
    """
    stationDataQuery = sq.text(
        f"""
        SELECT station_id, district FROM public.{DLY_STATIONS}
        WHERE district IS NOT NULL;
        """
    )

    stationData = pd.read_sql(stationDataQuery, conn)
    stationData[["district"]] = stationData[["district"]].astype(int)

    return stationData


if __name__ == "__main__":
    main()
