# -------------------------------------------
# DatasetJS.ipynb
#
# After all the data has been loaded and aggregated, this notebook creates the final datasets
#
# Required tables:
# -------------------------------------------
# - [COMBINED_WEATHER_TABLE](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_weather_combined)
# - [COPERNICUS_WEATHER_TABLE](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_day_copernicus_satellite_data)
# - [SOIL_MOISTURE_TABLE](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_soil_moisture)
# - [AGG_ERGOT_TABLE](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_ergot_sample_v2)
# - [ERGOT_SAMPLES_TABLE](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ergot_sample_feat_eng)
#
# Output:
# -------------------------------------------
# - [dataset_daily_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_daily_sat)
# - [dataset_weekly_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_weekly_sat)
# - [dataset_monthly_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_monthly_sat)
# - [dataset_cross_monthly_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_monthly_sat)
# - [dataset_cross_weekly_sat_JFMA](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_sat_JFMA)
# - [dataset_cross_weekly_sat_MAMJ](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_sat_MAMJ)
# - [dataset_cross_weekly_sat_MJJA](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_sat_MJJA)
# - [dataset_cross_weekly_sat_JASO](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_sat_JASO)
# - [dataset_daily_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_daily_station)
# - [dataset_weekly_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_weekly_station)
# - [dataset_monthly_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_monthly_station)
# - [dataset_cross_monthly_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_monthly_station)
# - [dataset_cross_weekly_station_JFMA](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_station_JFMA)
# - [dataset_cross_weekly_station_MAMJ](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_station_MAMJ)
# - [dataset_cross_weekly_station_MJJA](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_station_MJJA)
# - [dataset_cross_weekly_station_JASO](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_cross_weekly_station_JASO)
# - [dataset_daily_sat_soil](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_daily_sat_soil)
# - [dataset_weekly_sat_soil](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_weekly_sat_soil)
# - [dataset_monthly_sat_soil](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_monthly_sat_soil)
# - [dataset_daily_station_soil](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_daily_station_soil)
# - [dataset_weekly_station_soil](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_weekly_station_soil)
# - [dataset_monthly_station_soil](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_monthly_station_soil)
# -------------------------------------------
from datetime import datetime as dt
from dotenv import load_dotenv
import geopandas as gpd  # type: ignore
import sqlalchemy as sq
import pandas as pd
import numpy as np
import os, sys, calendar

import typing

sys.path.append("../")
from Shared.DataService import DataService


# Tables being used (see links in Required tables above)
COMBINED_WEATHER_TABLE = "agg_weather_combined"
COPERNICUS_WEATHER_TABLE = "agg_day_copernicus_satellite_data"
SOIL_MOISTURE_TABLE = "agg_soil_moisture"
AGG_ERGOT_TABLE = "agg_ergot_sample_v2"
ERGOT_SAMPLES_TABLE = "ergot_sample_feat_eng"

# Tables being created (see links in output above)
TABLESATSOILMDAILY = "dataset_daily_sat_soil"
TABLESATSOILMWEEKLY = "dataset_weekly_sat_soil"
TABLESATSOILMMONTHLY = "dataset_monthly_sat_soil"
TABLESTATIONSOILMDAILY = "dataset_daily_station_soil"
TABLESTATIONSOILMWEEKLY = "dataset_weekly_station_soil"
TABLESTATIONSOILMMONTHLY = "dataset_monthly_station_soil"
TABLESATDAILY = "dataset_daily_sat"
TABLESATWEEKLY = "dataset_weekly_sat"
TABLESATMONTHLY = "dataset_monthly_sat"
TABLESTATIONDAILY = "dataset_daily_station"
TABLESTATIONWEEKLY = "dataset_weekly_station"
TABLESTATIONMONTHLY = "dataset_monthly_station"

TABLECROSSSATWEEKLYA = "dataset_cross_weekly_sat_JFMA"
TABLECROSSSATWEEKLYB = "dataset_cross_weekly_sat_MAMJ"
TABLECROSSSATWEEKLYC = "dataset_cross_weekly_sat_MJJA"
TABLECROSSSATWEEKLYD = "dataset_cross_weekly_sat_JASO"
TABLECROSSSTATIONWEEKLYA = "dataset_cross_weekly_station_JFMA"
TABLECROSSSTATIONWEEKLYB = "dataset_cross_weekly_station_MAMJ"
TABLECROSSSTATIONWEEKLYC = "dataset_cross_weekly_station_MJJA"
TABLECROSSSTATIONWEEKLYD = "dataset_cross_weekly_station_JASO"

TABLECROSSSATMONTHLY = "dataset_cross_monthly_sat"
TABLECROSSSTATIONMONTHLY = "dataset_cross_monthly_station"


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
    generateNoErgotTables()
    generateCrossWeeklyTables()
    generateCrossMonthlyTables()


def getConn():
    """
    Purpose:
    Get a connection to the database
    """
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        raise Exception("Missing required env var(s)")

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)

    return db.connect()


def pullWeatherStationData() -> pd.DataFrame:
    """
    Purpose:
    Loads the weather station data from the combined weather station data table

    Tables:
    - [agg_weather_combined](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_weather_combined)

    Psuedocode:
    - Get a connection to the database
    - Create the weather station data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    weatherDataQuery = sq.text(
        f"""
        SELECT * FROM public.{COMBINED_WEATHER_TABLE}
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()

    return df


def pullWeatherCopernicusData() -> pd.DataFrame:
    """
    Purpose:
    Loads the Copernicus data from the Copernicus weather data table

    Tables:
    - [agg_day_copernicus_satellite_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_day_copernicus_satellite_data)

    # Psuedocode:
    - Get a connection to the database
    - Create the Copernicus weather data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    weatherDataQuery = sq.text(
        f"""
        SELECT * FROM public.{COPERNICUS_WEATHER_TABLE}
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()

    return df


def pullSoilMoistureData() -> pd.DataFrame:
    """
    Purpose:
    Loads the soil moisture data from the Satellite soil moisture data table

    Tables:
    - [agg_soil_moisture](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_soil_moisture)

    Psuedocode:
    - Get a connection to the database
    - Create the soil moisture data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    weatherDataQuery = sq.text(
        f"""
        SELECT year, month, day, district, 
        soil_moisture_min, soil_moisture_max, soil_moisture_mean
        FROM public.{SOIL_MOISTURE_TABLE}
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()

    return df


def pullAggErgotData() -> pd.DataFrame:
    """
    Purpose:
    Loads the ergot data from the aggregated ergot data table

    Tables:
    - [agg_ergot_sample_v2](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_ergot_sample_v2)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    weatherDataQuery = sq.text(
        f"""
        SELECT year, district, 
            present_prev1, 
            present_prev2, 
            present_prev3, 
            sum_severity_prev1, 
            sum_severity_prev2, 
            sum_severity_prev3, 
            percnt_true_prev1,
            percnt_true_prev2,
            percnt_true_prev3,
            median_prev1,
            median_prev2,
            median_prev3
        FROM public.{AGG_ERGOT_TABLE}
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()

    return df


def pullIndividualErgotSampleData() -> pd.DataFrame:
    """
    Purpose:
    Loads the ergot data from the individual ergot sample data table

    Tables:
    - [ergot_sample_feat_eng](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ergot_sample_feat_eng)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    weatherDataQuery = sq.text(
        f"""
        SELECT * FROM public.{ERGOT_SAMPLES_TABLE}
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()

    return df


def addErgotData(df: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Loads the ergot data from the ergot sample data tables and join them together

    Tables:
    - [agg_ergot_sample_v2](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_ergot_sample_v2)
    - [ergot_sample_feat_eng](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ergot_sample_feat_eng)

    Psuedocode:
    - Get the ergot data
    - [Merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) the two DataFrames together on year and district
    """
    aggErgotDf = pullAggErgotData()
    ergotDf = pullIndividualErgotSampleData()

    # right join on year, district
    mergedDf = pd.merge(df, aggErgotDf, on=["year", "district"], how="right")
    mergedDf = pd.merge(mergedDf, ergotDf, on=["year", "district"], how="left")

    return mergedDf


def getDailySat() -> pd.DataFrame:
    """
    Purpose:
    Loads the Copernicus data from the Copernicus weather data table and preproccesses it

    Tables:
    - [agg_day_copernicus_satellite_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_day_copernicus_satellite_data)

    Psuedocode:
    - Load the Copernicus data
    - Convert the year, month and day to a date
    - Get the day of the year
    - Drop the date column we just created
    """
    df = pullWeatherCopernicusData()

    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["day_of_year"] = df["date"].dt.dayofyear
    df.drop(columns=["date"], inplace=True)

    return df


def getDailyStation() -> pd.DataFrame:
    """
    Purpose:
    Loads the Weather station data from the weather station data table and preproccesses it

    Tables:
    - [agg_weather_combined](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_weather_combined)

    Psuedocode:
    - Load the data
    - Convert the year, month and day to a date
    - Get the day of the year
    - Drop the date column we just created
    """
    df = pullWeatherStationData()

    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["day_of_year"] = df["date"].dt.dayofyear
    df.drop(columns=["date"], inplace=True)

    return df


def getDailySoil() -> pd.DataFrame:
    """
    Purpose:
    Loads the soil moisture data from the satellite soil moisture data table and preproccesses it

    Tables:
    - [agg_soil_moisture](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_soil_moisture)

    Psuedocode:
    - Load the data
    - Convert the year, month and day to a date
    - Get the day of the year
    - Drop the date column we just created
    """
    df = pullSoilMoistureData()

    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["day_of_year"] = df["date"].dt.dayofyear
    df.drop(columns=["date"], inplace=True)

    return df


def getWeeklySat(dailyDf: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the Copernicus weather data by week

    Pseudocode:
    - Add the week to the data
    - [Aggregate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) the data
      [by year, month, week of year and district](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
    """
    dailyDf["date"] = pd.to_datetime(dailyDf[["year", "month", "day"]])

    # add a week of year column
    dailyDf["week_of_year"] = dailyDf["date"].dt.isocalendar().week
    dailyDf = dailyDf.drop(columns=["date"])

    # aggregate by week of year year and district
    weeklyDf = (
        dailyDf.groupby(["year", "month", "week_of_year", "district"])
        .agg(
            {
                "min_dewpoint_temperature": "min",
                "min_temperature": "min",
                "min_evaporation_from_bare_soil": "min",
                "min_skin_reservoir_content": "min",
                "min_skin_temperature": "min",
                "min_snowmelt": "min",
                "min_soil_temperature_level_1": "min",
                "min_soil_temperature_level_2": "min",
                "min_soil_temperature_level_3": "min",
                "min_soil_temperature_level_4": "min",
                "min_surface_net_solar_radiation": "min",
                "min_surface_pressure": "min",
                "min_volumetric_soil_water_layer_1": "min",
                "min_volumetric_soil_water_layer_2": "min",
                "min_volumetric_soil_water_layer_3": "min",
                "min_volumetric_soil_water_layer_4": "min",
                "min_leaf_area_index_high_vegetation": "min",
                "min_leaf_area_index_low_vegetation": "min",
                "max_dewpoint_temperature": "max",
                "max_temperature": "max",
                "max_evaporation_from_bare_soil": "max",
                "max_skin_reservoir_content": "max",
                "max_skin_temperature": "max",
                "max_snowmelt": "max",
                "max_soil_temperature_level_1": "max",
                "max_soil_temperature_level_2": "max",
                "max_soil_temperature_level_3": "max",
                "max_soil_temperature_level_4": "max",
                "max_surface_net_solar_radiation": "max",
                "max_surface_pressure": "max",
                "max_volumetric_soil_water_layer_1": "max",
                "max_volumetric_soil_water_layer_2": "max",
                "max_volumetric_soil_water_layer_3": "max",
                "max_volumetric_soil_water_layer_4": "max",
                "max_leaf_area_index_high_vegetation": "max",
                "max_leaf_area_index_low_vegetation": "max",
                "mean_dewpoint_temperature": "mean",
                "mean_temperature": "mean",
                "mean_evaporation_from_bare_soil": "mean",
                "mean_skin_reservoir_content": "mean",
                "mean_skin_temperature": "mean",
                "mean_snowmelt": "mean",
                "mean_soil_temperature_level_1": "mean",
                "mean_soil_temperature_level_2": "mean",
                "mean_soil_temperature_level_3": "mean",
                "mean_soil_temperature_level_4": "mean",
                "mean_surface_net_solar_radiation": "mean",
                "mean_surface_pressure": "mean",
                "mean_volumetric_soil_water_layer_1": "mean",
                "mean_volumetric_soil_water_layer_2": "mean",
                "mean_volumetric_soil_water_layer_3": "mean",
                "mean_volumetric_soil_water_layer_4": "mean",
                "mean_leaf_area_index_high_vegetation": "mean",
                "mean_leaf_area_index_low_vegetation": "mean",
            }
        )
        .reset_index()
    )

    return weeklyDf


def getWeeklySoilMoisture(dailyDf: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the Satellite soil moisture data by week

    Pseudocode:
    - Add the week to the data
    - [Aggregate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) the data
      [by year, month, week of year and district](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
    """
    dailyDf["date"] = pd.to_datetime(dailyDf[["year", "month", "day"]])

    # add a week of year column
    dailyDf["week_of_year"] = dailyDf["date"].dt.isocalendar().week
    dailyDf = dailyDf.drop(columns=["date"])

    # aggregate by week of year year and district
    weeklyDf = (
        dailyDf.groupby(["year", "month", "week_of_year", "district"])
        .agg(
            {
                "soil_moisture_min": "min",
                "soil_moisture_max": "max",
                "soil_moisture_mean": "mean",
            }
        )
        .reset_index()
    )

    return weeklyDf


def getMonthlySat(dailyDf: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the Copernicus weather data by month

    Pseudocode:
    - [Aggregate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) the data
      [by year, month and district](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
    """
    monthlyDf = (
        dailyDf.groupby(["year", "month", "district"])
        .agg(
            {
                "min_dewpoint_temperature": "min",
                "min_temperature": "min",
                "min_evaporation_from_bare_soil": "min",
                "min_skin_reservoir_content": "min",
                "min_skin_temperature": "min",
                "min_snowmelt": "min",
                "min_soil_temperature_level_1": "min",
                "min_soil_temperature_level_2": "min",
                "min_soil_temperature_level_3": "min",
                "min_soil_temperature_level_4": "min",
                "min_surface_net_solar_radiation": "min",
                "min_surface_pressure": "min",
                "min_volumetric_soil_water_layer_1": "min",
                "min_volumetric_soil_water_layer_2": "min",
                "min_volumetric_soil_water_layer_3": "min",
                "min_volumetric_soil_water_layer_4": "min",
                "min_leaf_area_index_high_vegetation": "min",
                "min_leaf_area_index_low_vegetation": "min",
                "max_dewpoint_temperature": "max",
                "max_temperature": "max",
                "max_evaporation_from_bare_soil": "max",
                "max_skin_reservoir_content": "max",
                "max_skin_temperature": "max",
                "max_snowmelt": "max",
                "max_soil_temperature_level_1": "max",
                "max_soil_temperature_level_2": "max",
                "max_soil_temperature_level_3": "max",
                "max_soil_temperature_level_4": "max",
                "max_surface_net_solar_radiation": "max",
                "max_surface_pressure": "max",
                "max_volumetric_soil_water_layer_1": "max",
                "max_volumetric_soil_water_layer_2": "max",
                "max_volumetric_soil_water_layer_3": "max",
                "max_volumetric_soil_water_layer_4": "max",
                "max_leaf_area_index_high_vegetation": "max",
                "max_leaf_area_index_low_vegetation": "max",
                "mean_dewpoint_temperature": "mean",
                "mean_temperature": "mean",
                "mean_evaporation_from_bare_soil": "mean",
                "mean_skin_reservoir_content": "mean",
                "mean_skin_temperature": "mean",
                "mean_snowmelt": "mean",
                "mean_soil_temperature_level_1": "mean",
                "mean_soil_temperature_level_2": "mean",
                "mean_soil_temperature_level_3": "mean",
                "mean_soil_temperature_level_4": "mean",
                "mean_surface_net_solar_radiation": "mean",
                "mean_surface_pressure": "mean",
                "mean_volumetric_soil_water_layer_1": "mean",
                "mean_volumetric_soil_water_layer_2": "mean",
                "mean_volumetric_soil_water_layer_3": "mean",
                "mean_volumetric_soil_water_layer_4": "mean",
                "mean_leaf_area_index_high_vegetation": "mean",
                "mean_leaf_area_index_low_vegetation": "mean",
            }
        )
        .reset_index()
    )

    return monthlyDf


def getMonthlySoilMoisture(dailyDf: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the soil mositure data by month

    Pseudocode:
    - [Aggregate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) the data
      [by year, month and district](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
    """
    monthlyDf = (
        dailyDf.groupby(["year", "month", "district"])
        .agg(
            {
                "soil_moisture_min": "min",
                "soil_moisture_max": "max",
                "soil_moisture_mean": "mean",
            }
        )
        .reset_index()
    )

    return monthlyDf


def getWeeklyStation(dailyDf: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the weather station data by week

    Pseudocode:
    - Add the week to the data
    - [Aggregate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) the data
      [by year, month, week of year and district](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
    """
    dailyDf["date"] = pd.to_datetime(dailyDf[["year", "month", "day"]])

    # add a week of year column
    dailyDf["week_of_year"] = dailyDf["date"].dt.isocalendar().week
    dailyDf = dailyDf.drop(columns=["date"])

    # aggregate by week of year year and district
    weeklyDf = (
        dailyDf.groupby(["year", "month", "week_of_year", "district"])
        .agg(
            {
                "min_temp_x": "min",
                "max_temp_x": "max",
                "mean_temp_x": "mean",
                "min_dew_point_temp": "min",
                "max_dew_point_temp": "max",
                "mean_dew_point_temp": "mean",
                "min_humidex": "min",
                "max_humidex": "max",
                "mean_humidex": "mean",
                "min_precip": "min",
                "max_precip": "max",
                "mean_precip": "mean",
                "min_rel_humid": "min",
                "max_rel_humid": "max",
                "mean_rel_humid": "mean",
                "min_stn_press": "min",
                "max_stn_press": "max",
                "mean_stn_press": "mean",
                "min_visibility": "min",
                "max_visibility": "max",
                "mean_visibility": "mean",
                "max_temp_y": "max",
                "min_temp_y": "min",
                "mean_temp_y": "mean",
                "min_total_rain": "min",
                "max_total_rain": "max",
                "mean_total_rain": "mean",
                "min_total_snow": "min",
                "max_total_snow": "max",
                "mean_total_snow": "mean",
                "min_total_precip": "min",
                "max_total_precip": "max",
                "mean_total_precip": "mean",
                "min_snow_on_grnd": "min",
                "max_snow_on_grnd": "max",
                "mean_snow_on_grnd": "mean",
            }
        )
        .reset_index()
    )

    return weeklyDf


def getMonthlyStation(dailyDf: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Aggregate the weather station data by month

    Pseudocode:
    - [Aggregate](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) the data
      [by year, month and district](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
    """
    monthlyDf = (
        dailyDf.groupby(["year", "month", "district"])
        .agg(
            {
                "min_temp_x": "min",
                "max_temp_x": "max",
                "mean_temp_x": "mean",
                "min_dew_point_temp": "min",
                "max_dew_point_temp": "max",
                "mean_dew_point_temp": "mean",
                "min_humidex": "min",
                "max_humidex": "max",
                "mean_humidex": "mean",
                "min_precip": "min",
                "max_precip": "max",
                "mean_precip": "mean",
                "min_rel_humid": "min",
                "max_rel_humid": "max",
                "mean_rel_humid": "mean",
                "min_stn_press": "min",
                "max_stn_press": "max",
                "mean_stn_press": "mean",
                "min_visibility": "min",
                "max_visibility": "max",
                "mean_visibility": "mean",
                "max_temp_y": "max",
                "min_temp_y": "min",
                "mean_temp_y": "mean",
                "min_total_rain": "min",
                "max_total_rain": "max",
                "mean_total_rain": "mean",
                "min_total_snow": "min",
                "max_total_snow": "max",
                "mean_total_snow": "mean",
                "min_total_precip": "min",
                "max_total_precip": "max",
                "mean_total_precip": "mean",
                "min_snow_on_grnd": "min",
                "max_snow_on_grnd": "max",
                "mean_snow_on_grnd": "mean",
            }
        )
        .reset_index()
    )

    return monthlyDf


def pushChunkwise(df: pd.DataFrame, tablename: str) -> None:
    """
    Purpose:
    Stores data in the database in chunks

    Pseudocode:
    - Get a database connection
    - [Push the data to the database](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html)
    - Close the connection

    Remarks: Some of our large data has too many columns to fit into the database, thus, we store the data in chunks accross multiple tables instead to bypass this restriction
    """
    conn = getConn()

    df.to_sql(
        tablename,
        conn,
        schema="public",
        if_exists="append",
        index=False,
        chunksize=1000,
    )

    conn.close()


def generateNoErgotTables():
    """
    Purpose:
    Stores chunks of the tables with too many columns
    """
    pushChunkwise(pullWeatherCopernicusData(), TABLESATDAILY)

    pushChunkwise(pullWeatherStationData(), TABLESTATIONDAILY)

    pushChunkwise(getWeeklySat(pullWeatherCopernicusData()), TABLESATWEEKLY)

    pushChunkwise(getWeeklyStation(pullWeatherStationData()), TABLESTATIONWEEKLY)

    pushChunkwise(getMonthlySat(pullWeatherCopernicusData()), TABLESATMONTHLY)

    pushChunkwise(getMonthlyStation(pullWeatherStationData()), TABLESTATIONMONTHLY)

    mergeDf = pd.merge(
        getDailySat(),
        getDailySoil(),
        on=["year", "day_of_year", "district"],
        how="left",
    )
    pushChunkwise(mergeDf, TABLESATSOILMDAILY)

    mergeDf = pd.merge(
        getDailyStation(),
        getDailySoil(),
        on=["year", "day_of_year", "district"],
        how="left",
    )
    pushChunkwise(mergeDf, TABLESTATIONSOILMDAILY)

    weeklySat = getWeeklySat(getDailySat())
    weeklySoil = getWeeklySoilMoisture(getDailySoil())
    mergeDf = pd.merge(
        weeklySat, weeklySoil, on=["year", "week_of_year", "district"], how="left"
    )
    pushChunkwise(mergeDf, TABLESATSOILMWEEKLY)

    weeklyStation = getWeeklyStation(getDailyStation())
    weeklySoil = getWeeklySoilMoisture(getDailySoil())
    mergeDf = pd.merge(
        weeklyStation, weeklySoil, on=["year", "week_of_year", "district"], how="left"
    )
    pushChunkwise(mergeDf, TABLESTATIONSOILMWEEKLY)

    monthlySat = getMonthlySat(getDailySat())
    monthlySoil = getMonthlySoilMoisture(getDailySoil())
    mergeDf = pd.merge(
        monthlySat, monthlySoil, on=["year", "month", "district"], how="left"
    )
    pushChunkwise(mergeDf, TABLESATSOILMMONTHLY)

    monthlyStation = getMonthlyStation(getDailyStation())
    monthlySoil = getMonthlySoilMoisture(getDailySoil())
    mergeDf = pd.merge(
        monthlyStation, monthlySoil, on=["year", "month", "district"], how="left"
    )
    pushChunkwise(mergeDf, TABLESTATIONSOILMMONTHLY)


def getDatasetDailySat() -> pd.DataFrame:
    """
    Purpose:
    Loads the daily Copernicus satellite data from the daily Copernicus satellite data table

    Tables:
    - [dataset_daily_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_daily_sat)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    query = sq.text(
        f"""
        SELECT * FROM public.{TABLESATDAILY}
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def getDatasetDailyStation() -> pd.DataFrame:
    """
    Purpose:
    Loads the daily weather station data from the daily weather station data table

    Tables:
    - [dataset_daily_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_daily_station)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    query = sq.text(
        f"""
        SELECT * FROM public.{TABLESTATIONDAILY}
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def getDatasetWeeklySat() -> pd.DataFrame:
    """
    Purpose:
    Loads the weekly Copernicus data from the weekly Copernicus satellite weather data table

    Tables:
    - [dataset_weekly_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_weekly_sat)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    query = sq.text(
        f"""
        SELECT * FROM public.{TABLESATWEEKLY}
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def getDatasetWeeklyStation() -> pd.DataFrame:
    """
    Purpose:
    Loads the weekly weather station data from the weekly weather station data table

    Tables:
    - [dataset_weekly_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_weekly_station)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    query = sq.text(
        f"""
        SELECT * FROM public.{TABLESTATIONWEEKLY}
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def getDatasetMonthlySat() -> pd.DataFrame:
    """
    Purpose:
    Loads the monthly Copernicus data from the monthly Copernicus satellite weather data table

    Tables:
    - [dataset_monthly_sat](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_monthly_sat)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    query = sq.text(
        f"""
        SELECT * FROM public.{TABLESATMONTHLY}
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def getDatasetMonthlyStation() -> pd.DataFrame:
    """
    Purpose:
    Loads the monthly weather station data from the monthly weather station data table

    Tables:
    - [dataset_monthly_station](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#dataset_monthly_station)

    Psuedocode:
    - Get a connection to the database
    - Create the ergot data SQL query
    - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)
    - Close the database connection
    """
    conn = getConn()
    query = sq.text(
        f"""
        SELECT * FROM public.{TABLESTATIONMONTHLY}
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def crossWeekOfYear(
    df: pd.DataFrame, weekRange: typing.List[int], exclude: typing.List[str]
) -> pd.DataFrame:
    """
    Purpose:
    We create a table where each row is a district and each column is a week of the year crossed with a weather attribute the columns are labeled as such: attribute_week_of_year the weekRange is a list of ints that represent the weeks of the year we want to include in the table

    Pseudocode:
    - Drop columns that do not fit into the week range
    - Get the names of all the columns
    - Remove the irrelevant columns (these are the columns we wont want to appear once our data has been reshaped)
    - Get the unique years and districts in remaining data
    - Grab all attributes and establish them as key in a dictionary
    - Once finished for the current date, district combination, store the dictionary into a list

    Remark: for this function to work correctly the following columns must be present: year, district and week

    Also note that we use a list of dictionaries since it is much faster to do so as opposed to the number of DataFrame manipulations we'd require otherwise
    """

    # keep only rows that are in the weekRange
    df = df.loc[df["week_of_year"].isin(weekRange)]

    # get the columns we will want to pull information from
    cols = df.columns.tolist()  # type: ignore
    for col in exclude:
        cols.remove(col)

    years = df["year"].unique().tolist()  # type: ignore
    districts = df["district"].unique().tolist()  # type: ignore

    listForDF = []  # list of dictionaries that will be used to create the dataframe
    for year in years:
        for district in districts:
            currData = {}  # for each year/district combination create a dictionary

            # adds the year and district
            currData["year"] = year
            currData["district"] = district

            # for each day we want to grab all attributes and establish them as columns i.e MO-DA:attribute
            for week in weekRange:
                # grab the row from the aggregated df
                currRow = df.loc[
                    (df["year"] == year)
                    & (df["week_of_year"] == week)
                    & (df["district"] == district)
                ]

                for col in cols:  # parse each of the desired columns
                    currAttr = f"{week}:{col}"  # the current attribute which corresponds to the date and the column
                    currVal = 0  # defaults as zero incase it does not exist

                    if len(currRow[col]) == 1:
                        # the current value from the loaded data
                        currVal = currRow[col].item()

                    currData[currAttr] = currVal

            listForDF.append(currData)

    return pd.DataFrame(listForDF)


def crossMonthOfYear(
    df: pd.DataFrame, monthRange: typing.List[int], exclude: typing.List[str]
) -> pd.DataFrame:
    """
    Purpose:
    We create a table where each row is a district and each column is a month of the year crossed with a weather attribute the columns are labeled as such: attribute_month_of_year the monthRange is a list of ints that represent the months of the year we want to include in the table

    Pseudocode:
    - Drop columns that do not fit into the month range
    - Get the names of all the columns
    - Remove the irrelevant columns (these are the columns we wont want to appear once our data has been reshaped)
    - Get the unique years and districts in remaining data
    - Grab all attributes and establish them as key in a dictionary
    - Once finished for the current date, district combination, store the dictionary into a list

    Remark: for this function to work correctly the following columns must be present: year, district and month

    Also note that we use a list of dictionaries since it is much faster to do so as opposed to the number of DataFrame manipulations we'd require otherwise
    """

    # keep only rows that are in the monthRange
    df = df.loc[df["month"].isin(monthRange)]

    # get the columns we will want to pull information from
    cols = df.columns.tolist()  # type: ignore
    for col in exclude:
        cols.remove(col)

    years = df["year"].unique().tolist()  # type: ignore
    districts = df["district"].unique().tolist()  # type: ignore

    listForDF = []  # list of dictionaries that will be used to create the dataframe
    for year in years:
        for district in districts:
            currData = {}
            currData["year"] = year
            currData["district"] = district

            for month in monthRange:
                currRow = df.loc[
                    (df["year"] == year)
                    & (df["month"] == month)
                    & (df["district"] == district)
                ]

                for col in cols:
                    currAttr = f"{month}:{col}"
                    currVal = 0

                    if len(currRow[col]) == 1:
                        currVal = currRow[col].item()

                    currData[currAttr] = currVal

            listForDF.append(currData)

    return pd.DataFrame(listForDF)


def generateCrossWeeklyTables():
    """
    Purpose:
    Crosses weekly data against the year to help determine the importance of each parameter of each week is to the model which is then stored in the database
    """

    # weekly jan feb mar apr
    weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    crossedDf = crossWeekOfYear(
        getDatasetWeeklySat(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSATWEEKLYA)

    crossedDf = crossWeekOfYear(
        getDatasetWeeklyStation(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSTATIONWEEKLYA)

    # weekly mar apr may jun
    weeks = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    crossedDf = crossWeekOfYear(
        getDatasetWeeklySat(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSATWEEKLYB)

    crossedDf = crossWeekOfYear(
        getDatasetWeeklyStation(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSTATIONWEEKLYB)

    # weekly may jun jul aug
    weeks = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
    crossedDf = crossWeekOfYear(
        getDatasetWeeklySat(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSATWEEKLYC)

    crossedDf = crossWeekOfYear(
        getDatasetWeeklyStation(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSTATIONWEEKLYC)

    # weekly jul aug sep oct
    weeks = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
    crossedDf = crossWeekOfYear(
        getDatasetWeeklySat(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSATWEEKLYD)

    crossedDf = crossWeekOfYear(
        getDatasetWeeklyStation(), weeks, ["year", "district", "month", "week_of_year"]
    )
    pushChunkwise(crossedDf, TABLECROSSSTATIONWEEKLYD)


def generateCrossMonthlyTables():
    """
    Purpose:
    Crosses monthly data against the year to help determine the importance of each parameter of each month is to the model which is then stored in the database
    """

    # monthly
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    crossedDf = crossMonthOfYear(
        getDatasetMonthlySat(), months, ["year", "district", "month"]
    )
    pushChunkwise(crossedDf, TABLECROSSSATMONTHLY)

    crossedDf = crossMonthOfYear(
        getDatasetMonthlyStation(), months, ["year", "district", "month"]
    )
    pushChunkwise(crossedDf, TABLECROSSSTATIONMONTHLY)


if __name__ == "__main__":
    main()
