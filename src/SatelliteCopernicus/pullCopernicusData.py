# %%
import os
import sys
import time
import random
import zipfile
import calendar
import multiprocessing as mp
import cdsapi  # type: ignore
from dotenv import load_dotenv
import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import xarray as xr  # type: ignore
import pandas as pd
import numpy as np
import black
import jupyter_black as bl  # type: ignore
from datetime import datetime
from CopernicusQueryBuilder import CopernicusQueryBuilder

sys.path.append("../")
from Shared.DataService import DataService 

# %%

LOG_FILE = "data/scrape_copernicus_parallel.log"
ERROR_FILE = "data/scrape_copernicus_parallel.err"

bl.load()
load_dotenv("../docker/.env")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")

# %%
NUM_WORKERS = 1  # The number of workers we want to employ (maximum is 16 as per the number of cores)
REQ_DELAY = 60  # 1 minute - the base delay required to bypass pulling limits
MIN_DELAY = 60  # 1 minute - once added to the required delay, creates a minimum delay of 5 minutes to bypass pulling limits
MAX_DELAY = 180  # 3 minutes - once added to the required delay, creates a maximum delay of 5 minutes to bypass pulling limits
TABLE = "copernicus_satellite_data"

MIN_MONTH = 1
MAX_MONTH = 12

MIN_YEAR = 1995
MAX_YEAR = 2023

years = [
    str(year) for year in range(MIN_YEAR, MAX_YEAR + 1)
]  # the year range we want to pull data from
months = [
    str(month) for month in range(MIN_MONTH, MAX_MONTH + 1)
]  # the month range we want to pull data from

ATTRS = [  # the attributes we want to pull data for
    "2m_dewpoint_temperature",
    "2m_temperature",
    "evaporation_from_bare_soil",
    "skin_reservoir_content",
    "skin_temperature",
    "snowmelt",
    "soil_temperature_level_1",
    "soil_temperature_level_2",
    "soil_temperature_level_3",
    "soil_temperature_level_4",
    "surface_net_solar_radiation",
    "surface_pressure",
    "volumetric_soil_water_layer_1",
    "volumetric_soil_water_layer_2",
    "volumetric_soil_water_layer_3",
    "volumetric_soil_water_layer_4",
    "leaf_area_index_high_vegetation",
    "leaf_area_index_low_vegetation",
]

HOURS = [
    "00:00",
    "01:00",
    "02:00",
    "03:00",
    "04:00",
    "05:00",
    "06:00",
    "07:00",
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
    "22:00",
    "23:00",
]

AREA = [61, -125, 48, -88]


# %%
def updateLog(fileName: str, message: str) -> None:
    if fileName is not None:
        with open(fileName, "a") as log:
            log.write(message + "\n")
            log.close()
    print(message)


# %%
# loads the agriculture regions from the datbase (projection is EPSG:3347)
def loadGeometry(conn: sq.engine.Connection) -> gpd.GeoDataFrame:
    query = sq.text("select cr_num, geometry FROM public.census_ag_regions")
    agRegions = gpd.GeoDataFrame.from_postgis(
        query, conn, crs="EPSG:3347", geom_col="geometry"
    )

    return agRegions


# %%
def addDateAttrs(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    try:
        for index in range(len(df.index)):
            date = pd.Timestamp(np.datetime64(df.at[index, "datetime"]))
            df.at[index, "year"] = date.year
            df.at[index, "month"] = date.month
            df.at[index, "day"] = date.day
            df.at[index, "hour"] = date.hour

        df[["year", "month", "day", "hour"]] = df[
            ["year", "month", "day", "hour"]
        ].astype(int)
    except Exception as e:
        print(f"[ERROR] {e}")

    return df


# %%
def addRegions(df: pd.DataFrame, agRegions: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Creates geometry from df using lon and lat as cords to create points (points being geometry)
    df = gpd.GeoDataFrame(
        df, crs="EPSG:4326", geometry=gpd.points_from_xy(df.lon, df.lat)
    )

    # Changes the points projection to match the agriculture regions of EPSG:3347
    df.to_crs(crs="EPSG:3347", inplace=True)  # type: ignore

    # Join the two dataframes based on which points fit within what agriculture regions
    df = gpd.sjoin(df, agRegions, how="left", predicate="within")

    df.drop(columns=["geometry", "index_right"], inplace=True)
    df = df[df["cr_num"].notna()]  # Take rows that are valid numbers
    df[["cr_num"]] = df[["cr_num"]].astype(int)

    return df


# %%
def unzipFile(file: str):
    with zipfile.ZipFile(f"./{file}.netcdf.zip", "r") as zip_ref:  # Opens the zip file
        # Collects the information of each file contained within
        zipinfos = zip_ref.infolist()

        for zipinfo in zipinfos:  # For each file in the zip file (we only expect one)
            zipinfo.filename = f"{file}.nc"  # Changes the unzipped files name (once its unzipped of course)
            zip_ref.extract(zipinfo)  # Unzips the file
            break


# %%
def readNetCDF(file: str) -> pd.DataFrame:
    dataset = xr.open_dataset(f"./{file}.nc")  # Loads the dataset from the netcdf file
    # Converts the contents into a dataframe and corrects indexes
    df = dataset.to_dataframe().reset_index()

    dataset.close()

    return df


# %%
def formatDF(df: pd.DataFrame) -> pd.DataFrame:
    # Adds the remaining attributes we want to store which will be gathered during data preprocessing
    df["year"] = None
    df["month"] = None
    df["day"] = None
    df["hour"] = None

    # Renames the dataframes columns so it can be matched when its posted to the database
    df.rename(columns={df.columns[0]: "lon"}, inplace=True)
    df.rename(columns={df.columns[1]: "lat"}, inplace=True)
    df.rename(columns={df.columns[2]: "datetime"}, inplace=True)
    df.rename(columns={df.columns[3]: "dewpoint_temperature"}, inplace=True)
    df.rename(columns={df.columns[4]: "temperature"}, inplace=True)
    df.rename(columns={df.columns[5]: "evaporation_from_bare_soil"}, inplace=True)
    df.rename(columns={df.columns[6]: "skin_reservoir_content"}, inplace=True)
    df.rename(columns={df.columns[7]: "skin_temperature"}, inplace=True)
    df.rename(columns={df.columns[8]: "snowmelt"}, inplace=True)
    df.rename(columns={df.columns[9]: "soil_temperature_level_1"}, inplace=True)
    df.rename(columns={df.columns[10]: "soil_temperature_level_2"}, inplace=True)
    df.rename(columns={df.columns[11]: "soil_temperature_level_3"}, inplace=True)
    df.rename(columns={df.columns[12]: "soil_temperature_level_4"}, inplace=True)
    df.rename(columns={df.columns[13]: "surface_net_solar_radiation"}, inplace=True)
    df.rename(columns={df.columns[14]: "surface_pressure"}, inplace=True)
    df.rename(columns={df.columns[15]: "volumetric_soil_water_layer_1"}, inplace=True)
    df.rename(columns={df.columns[16]: "volumetric_soil_water_layer_2"}, inplace=True)
    df.rename(columns={df.columns[17]: "volumetric_soil_water_layer_3"}, inplace=True)
    df.rename(columns={df.columns[18]: "volumetric_soil_water_layer_4"}, inplace=True)
    df.rename(columns={df.columns[19]: "leaf_area_index_high_vegetation"}, inplace=True)
    df.rename(columns={df.columns[20]: "leaf_area_index_low_vegetation"}, inplace=True)

    # Used to detect null values - na.mask, null etc... will be replaced with nan which get removed immediately after
    df[
        [
            "lon",
            "lat",
            "dewpoint_temperature",
            "temperature",
            "evaporation_from_bare_soil",
            "skin_reservoir_content",
            "skin_temperature",
            "snowmelt",
            "soil_temperature_level_1",
            "soil_temperature_level_2",
            "soil_temperature_level_3",
            "soil_temperature_level_4",
            "surface_net_solar_radiation",
            "surface_pressure",
            "volumetric_soil_water_layer_1",
            "volumetric_soil_water_layer_2",
            "volumetric_soil_water_layer_3",
            "volumetric_soil_water_layer_4",
            "leaf_area_index_high_vegetation",
            "leaf_area_index_low_vegetation",
        ]
    ] = df[
        [
            "lon",
            "lat",
            "dewpoint_temperature",
            "temperature",
            "evaporation_from_bare_soil",
            "skin_reservoir_content",
            "skin_temperature",
            "snowmelt",
            "soil_temperature_level_1",
            "soil_temperature_level_2",
            "soil_temperature_level_3",
            "soil_temperature_level_4",
            "surface_net_solar_radiation",
            "surface_pressure",
            "volumetric_soil_water_layer_1",
            "volumetric_soil_water_layer_2",
            "volumetric_soil_water_layer_3",
            "volumetric_soil_water_layer_4",
            "leaf_area_index_high_vegetation",
            "leaf_area_index_low_vegetation",
        ]
    ].astype(
        float
    )

    return df


# %%
def pullSatelliteData(
    agRegions: gpd.GeoDataFrame,
    delay: int,
    year: str,
    month: str,
    days: list,
    outputFile: str,
):
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        updateLog(ERROR_FILE, "Environment variables not set")
        raise ValueError("Environment variables not set")

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    time.sleep(delay)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updateLog(LOG_FILE, f"{timestamp}Starting to pull data for {year}/{month}")
    conn = db.connect()
    c = cdsapi.Client()

    try:
        c.retrieve(
            "reanalysis-era5-land",
            {
                "format": "netcdf.zip",
                "variable": ATTRS,
                "year": year,
                "month": month,
                "day": days,
                "time": HOURS,
                "area": AREA,
            },
            f"{outputFile}.netcdf.zip",
        )

        # Unzips the file, renames it to outputFile and then deletes the source .zip file
        unzipFile(outputFile)

        df = readNetCDF(outputFile)  # Converts the netcdf content into a dataframe
        # Formats the data frame to process null values, add additional attributes and rename columns

        df = formatDF(df)

        updateLog(LOG_FILE, f"Starting to match regions for data in {year}/{month}")
        # Links data to their crop district number (stored in cr_num)
        df = addRegions(df, agRegions)
        df = df.reset_index()
        updateLog(
            LOG_FILE,
            f"Finished matching {len(df.index)} regions for data in {year}/{month}",
        )

        # Breaks down the date attributes into its components and saves them for storage
        df = addDateAttrs(df)
        updateLog(LOG_FILE, f"Added date attributes for {year}/{month}")

        updateLog(LOG_FILE, f"Adding data from {year}/{month} to the Database")
        df.drop(columns=["index"], inplace=True)
        df.to_sql(TABLE, conn, schema="public", if_exists="append", index=False)
    except Exception as e:
        updateLog(ERROR_FILE, f"Error pulling data for {year}/{month} : {e}")

    # Clean up the environment after the transaction
    try:
        os.remove(f"{outputFile}.nc")
        os.remove(f"{outputFile}.netcdf.zip")
    except Exception as e:
        updateLog(ERROR_FILE, f"Error cleaning up {year}/{month} : {e}")

    db.cleanup()
    updateLog(LOG_FILE, f"Finished adding data from {year}/{month} to the Database")


# %%
def main():
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        raise ValueError("Environment variables not set")

    # Handles connections to the database
    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    queryHandler = CopernicusQueryBuilder()
    jobArgs = []  # Holds tuples of arguments for pooled workers
    count = 1  # An incrementer used to create unique file names

    conn = db.connect()  # Connect to the database
    queryHandler.createCopernicusTableReq(db)

    # Load the agriculture region geometries from the database
    agRegions = loadGeometry(conn)
    db.cleanup()  # Disconnect from the database (workers maintain their own connections)

    # Creates the list of arguments (stored as tuples) used in the multiple processes for pullSateliteData(agRegions, year, month, days, outputFile)
    for year in years:
        for month in months:
            # Calculates the number of days - stored in index 1 of a tuple
            numDays = calendar.monthrange(int(year), int(month))[1]

            # calculates a random delay (asc for groups of 12)
            delay = (count % NUM_WORKERS != 0) * (
                REQ_DELAY * (count % NUM_WORKERS) + random.randint(MIN_DELAY, MAX_DELAY)
            )

            days = [str(day) for day in range(1, numDays + 1)]
            outputFile = f"copernicus{count}"
            count += 1

            jobArgs.append(tuple((agRegions, delay, year, month, days, outputFile)))

    # Handles the multiple processes
    pool = mp.Pool(NUM_WORKERS)  # Defines the number of workers

    # Creates the queue of jobs - pullSateliteData is the function and jobArgs holds the arguments
    pool.starmap(pullSatelliteData, jobArgs)
    pool.close()  # Once these jobs are finished close the multiple processes pool


# %%
if __name__ == "__main__":
    main()
