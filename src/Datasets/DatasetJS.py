# %%
import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os, sys, calendar
from datetime import datetime as dt

sys.path.append("../")
from Shared.DataService import DataService

# %%
load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")

# %%


# %%
def pullWeatherStationData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.agg_weather_combined
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def pullWeatherCopernicusData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.agg_day_copernicus_satellite_data
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def pullSoilMoistureData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT year, month, day, district, 
        soil_moisture_min, soil_moisture_max, soil_moisture_mean
        FROM public.agg_soil_moisture
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def pullAggErgotData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
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
        FROM public.agg_ergot_sample_v2
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def pullIndividualErgotSampleData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.ergot_sample_feat_eng
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def addErgotData(df: pd.DataFrame) -> pd.DataFrame:
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
    aggErgotDf = pullAggErgotData(conn)
    ergotDf = pullIndividualErgotSampleData(conn)

    # right join on year, district
    mergedDf = pd.merge(df, aggErgotDf, on=["year", "district"], how="right")
    mergedDf = pd.merge(mergedDf, ergotDf, on=["year", "district"], how="left")
    conn.close()
    return mergedDf


# %%
def getDailySatSoil() -> pd.DataFrame:
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

    satelliteDf = pullWeatherCopernicusData(conn)
    soilDf = pullSoilMoistureData(conn)

    # merge on year, month, day, district
    mergedDf = pd.merge(satelliteDf, soilDf, on=["year", "month", "day", "district"])

    mergedDf["date"] = pd.to_datetime(mergedDf[["year", "month", "day"]])
    # add day of year column
    mergedDf["day_of_year"] = mergedDf["date"].dt.dayofyear

    mergedDf = mergedDf.drop(columns=["date"])

    conn.close()
    return mergedDf


# %%
def getWeeklySatSoil(dailyDf: pd.DataFrame) -> pd.DataFrame:
    dailyDf["date"] = pd.to_datetime(dailyDf[["year", "month", "day"]])
    # add a week of year column
    dailyDf["week_of_year"] = dailyDf["date"].dt.isocalendar().week
    dailyDf = dailyDf.drop(columns=["date"])

    # aggregate by week of year year and district
    weeklyDf = dailyDf.groupby(["year", "week_of_year", "district"]).agg(
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
            "soil_moisture_min": "min",
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
            "soil_moisture_max": "max",
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
            "soil_moisture_mean": "mean",
        }
    )

    return weeklyDf


# %%
def getMonthlySatSoil(dailyDf: pd.DataFrame) -> pd.DataFrame:
    monthlyDf = dailyDf.groupby(["year", "month", "district"]).agg(
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
            "soil_moisture_min": "min",
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
            "soil_moisture_max": "max",
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
            "soil_moisture_mean": "mean",
        }
    )

    return monthlyDf


# %%
def getDailyStationSoil() -> pd.DataFrame:
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

    stationDf = pullWeatherStationData(conn)
    soilDf = pullSoilMoistureData(conn)

    # merge on year, month, day, district
    mergedDf = pd.merge(stationDf, soilDf, on=["year", "month", "day", "district"])

    mergedDf["date"] = pd.to_datetime(mergedDf[["year", "month", "day"]])
    # add day of year column
    mergedDf["day_of_year"] = mergedDf["date"].dt.dayofyear

    mergedDf = mergedDf.drop(columns=["date"])

    conn.close()
    return mergedDf


# %%
def getWeeklyStationSoil(dailyDf: pd.DataFrame) -> pd.DataFrame:
    dailyDf["date"] = pd.to_datetime(dailyDf[["year", "month", "day"]])
    # add a week of year column
    dailyDf["week_of_year"] = dailyDf["date"].dt.isocalendar().week
    dailyDf = dailyDf.drop(columns=["date"])

    # aggregate by week of year year and district
    weeklyDf = dailyDf.groupby(["year", "week_of_year", "district"]).agg(
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
            "soil_moisture_min": "min",
            "soil_moisture_max": "max",
            "soil_moisture_mean": "mean",
        }
    )
    return weeklyDf


# %%
def getMonthlyStationSoil(dailyDf: pd.DataFrame) -> pd.DataFrame:
    monthlyDf = dailyDf.groupby(["year", "month", "district"]).agg(
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
            "soil_moisture_min": "min",
            "soil_moisture_max": "max",
            "soil_moisture_mean": "mean",
        }
    )
    return monthlyDf


# %%
def generateSatelliteWeatherDatasetCSVs():
    TABLEDAILY = "dataset_daily_sat_soil_ergot"
    TABLEWEEKLY = "dataset_weekly_sat_soil_ergot"
    TABLEMONTHLY = "dataset_monthly_sat_soil_ergot"
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

    dailyDf = getDailySatSoil()
    dailyDf = addErgotData(dailyDf)
    # dailyDf.to_sql(TABLEDAILY, conn, schema="public", if_exists="replace", index=False)
    dailyDf.to_csv("data/daily_sat_soil_ergot.csv", index=False)

    dailyDf = getDailySatSoil()
    weeklyDf = getWeeklySatSoil(dailyDf)
    weeklyDf = addErgotData(weeklyDf)
    # weeklyDf.to_sql(TABLEWEEKLY, conn, schema="public", if_exists="replace", index=False)
    weeklyDf.to_csv("data/weekly_sat_soil_ergot.csv", index=False)

    dailyDf = getDailySatSoil()
    monthlyDf = getMonthlySatSoil(dailyDf)
    monthlyDf = addErgotData(monthlyDf)
    # monthlyDf.to_sql(TABLEMONTHLY, conn, schema="public", if_exists="replace", index=False)
    monthlyDf.to_csv("data/monthly_sat_soil_ergot.csv", index=False)

    conn.close()


# %%
def generateStationWeatherDatasetCSVs():
    TABLEDAILY = "dataset_daily_station_soil_ergot"
    TABLEWEEKLY = "dataset_weekly_station_soil_ergot"
    TABLEMONTHLY = "dataset_monthly_station_soil_ergot"
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

    dailyDf = getDailyStationSoil()
    dailyDf = addErgotData(dailyDf)
    # dailyDf.to_sql(TABLEDAILY, conn, schema="public", if_exists="replace", index=False)
    dailyDf.to_csv("data/daily_station_ergot.csv", index=False)

    dailyDf = getDailyStationSoil()
    weeklyDf = getWeeklyStationSoil(dailyDf)
    weeklyDf = addErgotData(weeklyDf)
    # weeklyDf.to_sql(TABLEWEEKLY, conn, schema="public", if_exists="replace", index=False)
    weeklyDf.to_csv("data/weekly_station_ergot.csv", index=False)

    dailyDf = getDailyStationSoil()
    monthlyDf = getMonthlyStationSoil(dailyDf)
    monthlyDf = addErgotData(monthlyDf)
    # monthlyDf.to_sql(TABLEMONTHLY, conn, schema="public", if_exists="replace", index=False)
    monthlyDf.to_csv("data/monthly_station_ergot.csv", index=False)

    conn.close()


# %%
def pushCsvToDB(filename: str, tablename: str) -> None:
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

    for df in pd.read_csv(filename, chunksize=1000):
        df.to_sql(tablename, conn, schema="public", if_exists="append", index=False)

    conn.close()


# %%
def pushCSV():
    pushCsvToDB("data/daily_sat_soil_ergot.csv", "dataset_daily_sat_soil_ergot")
    pushCsvToDB("data/weekly_sat_soil_ergot.csv", "dataset_weekly_sat_soil_ergot")
    pushCsvToDB("data/monthly_sat_soil_ergot.csv", "dataset_monthly_sat_soil_ergot")
    pushCsvToDB("data/daily_station_ergot.csv", "dataset_daily_station_soil_ergot")
    pushCsvToDB("data/weekly_station_ergot.csv", "dataset_weekly_station_soil_ergot")
    pushCsvToDB("data/monthly_station_ergot.csv", "dataset_monthly_station_soil_ergot")


# %%
if __name__ == "__main__":
    # generateSatelliteWeatherDatasetCSVs()
    generateStationWeatherDatasetCSVs()
    pushCSV()

# %%
