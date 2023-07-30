# %%
import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os, sys, calendar
from datetime import datetime as dt
import typing

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
def getConn():
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


# %%
def pullWeatherStationData() -> pd.DataFrame:
    # pulling weather station data from the database
    conn = getConn()
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.agg_weather_combined
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()
    return df


# %%
def pullWeatherCopernicusData() -> pd.DataFrame:
    # pulling weather station data from the database
    conn = getConn()
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.agg_day_copernicus_satellite_data
        """
    )

    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()
    return df


# %%
def pullSoilMoistureData() -> pd.DataFrame:
    # pulling weather station data from the database
    conn = getConn()
    weatherDataQuery = sq.text(
        """
        SELECT year, month, day, district, 
        soil_moisture_min, soil_moisture_max, soil_moisture_mean
        FROM public.agg_soil_moisture
        """
    )
    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()
    return df


# %%
def pullAggErgotData() -> pd.DataFrame:
    # pulling weather station data from the database
    conn = getConn()
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
    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()
    return df


# %%
def pullIndividualErgotSampleData() -> pd.DataFrame:
    # pulling weather station data from the database
    conn = getConn()
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.ergot_sample_feat_eng
        """
    )
    df = pd.read_sql(weatherDataQuery, conn)
    conn.close()
    return df


# %%
def addErgotData(df: pd.DataFrame) -> pd.DataFrame:
    conn = getConn()
    aggErgotDf = pullAggErgotData()
    ergotDf = pullIndividualErgotSampleData()

    # right join on year, district
    mergedDf = pd.merge(df, aggErgotDf, on=["year", "district"], how="right")
    mergedDf = pd.merge(mergedDf, ergotDf, on=["year", "district"], how="left")
    conn.close()
    return mergedDf


# %%
def getDailySat() -> pd.DataFrame:
    df = pullWeatherCopernicusData()
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["day_of_year"] = df["date"].dt.dayofyear
    df.drop(columns=["date"], inplace=True)
    return df


# %%
def getDailyStation() -> pd.DataFrame:
    df = pullWeatherStationData()
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["day_of_year"] = df["date"].dt.dayofyear
    df.drop(columns=["date"], inplace=True)
    return df


# %%
def getDailySoil() -> pd.DataFrame:
    df = pullSoilMoistureData()
    df["date"] = pd.to_datetime(df[["year", "month", "day"]])
    df["day_of_year"] = df["date"].dt.dayofyear
    df.drop(columns=["date"], inplace=True)
    return df


# %%
def getWeeklySat(dailyDf: pd.DataFrame) -> pd.DataFrame:
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


# %%
def getWeeklySoilMoisture(dailyDf: pd.DataFrame) -> pd.DataFrame:
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


# %%
def getMonthlySat(dailyDf: pd.DataFrame) -> pd.DataFrame:
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


# %%
def getMonthlySoilMoisture(dailyDf: pd.DataFrame) -> pd.DataFrame:
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


# %%
def getWeeklyStation(dailyDf: pd.DataFrame) -> pd.DataFrame:
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


# %%
def getMonthlyStation(dailyDf: pd.DataFrame) -> pd.DataFrame:
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


# %%
def pushChunkwise(df: pd.DataFrame, tablename: str) -> None:
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


# %%
def generateNoErgotTables():
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


# %%
def getDatasetDailySat() -> pd.DataFrame:
    conn = getConn()

    query = sq.text(
        """
        SELECT * FROM public.dataset_daily_sat
        """
    )

    df = pd.read_sql(query, conn)

    conn.close()
    return df


# %%
def getDatasetDailyStation() -> pd.DataFrame:
    conn = getConn()

    query = sq.text(
        """
        SELECT * FROM public.dataset_daily_station
        """
    )

    df = pd.read_sql(query, conn)

    conn.close()
    return df


# %%
def getDatasetWeeklySat() -> pd.DataFrame:
    conn = getConn()

    query = sq.text(
        """
        SELECT * FROM public.dataset_weekly_sat
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# %%
def getDatasetWeeklyStation() -> pd.DataFrame:
    conn = getConn()

    query = sq.text(
        """
        SELECT * FROM public.dataset_weekly_station
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# %%
def getDatasetMonthlySat() -> pd.DataFrame:
    conn = getConn()

    query = sq.text(
        """
        SELECT * FROM public.dataset_monthly_sat
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# %%
def getDatasetMonthlyStation() -> pd.DataFrame:
    conn = getConn()

    query = sq.text(
        """
        SELECT * FROM public.dataset_monthly_station
        """
    )

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# %%
def crossWeekOfYear(
    df: pd.DataFrame, weekRange: typing.List[int], exclude: typing.List[str]
) -> pd.DataFrame:
    """We create a table where each row is a district and each column is a week of the year crossed with a weather attribute"""
    """ the columns are labeled as such: attribute_week_of_year """
    """ the weekRange is a list of ints that represent the weeks of the year we want to include in the table """

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


# %%
def crossMonthOfYear(
    df: pd.DataFrame, monthRange: typing.List[int], exclude: typing.List[str]
) -> pd.DataFrame:
    """We create a table where each row is a district and each column is a month of the year crossed with a weather attribute"""
    """ the columns are labeled as such: attribute_month_of_year """
    """ the monthRange is a list of ints that represent the months of the year we want to include in the table """

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


# %%
def generateCrossWeeklyTables():
    TABLECROSSSATWEEKLYA = "dataset_cross_weekly_sat_JFMA"
    TABLECROSSSATWEEKLYB = "dataset_cross_weekly_sat_MAMJ"
    TABLECROSSSATWEEKLYC = "dataset_cross_weekly_sat_MJJA"
    TABLECROSSSATWEEKLYD = "dataset_cross_weekly_sat_JASO"
    TABLECROSSSTATIONWEEKLYA = "dataset_cross_weekly_station_JFMA"
    TABLECROSSSTATIONWEEKLYB = "dataset_cross_weekly_station_MAMJ"
    TABLECROSSSTATIONWEEKLYC = "dataset_cross_weekly_station_MJJA"
    TABLECROSSSTATIONWEEKLYD = "dataset_cross_weekly_station_JASO"

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


# %%
def generateCrossMonthlyTables():
    TABLECROSSSATMONTHLY = "dataset_cross_monthly_sat"
    TABLECROSSSTATIONMONTHLY = "dataset_cross_monthly_station"

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


# %%
def generateFeatureCrossTables():
    generateCrossWeeklyTables()
    generateCrossMonthlyTables()


# %%
if __name__ == "__main__":
    generateNoErgotTables()
    generateFeatureCrossTables()
