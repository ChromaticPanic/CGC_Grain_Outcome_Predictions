# -------------------------------------------
# PullMoistureData.ipynb
#
# After [agriculture regions have been loaded](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/WeatherStation/importBoundariesAndStations.ipynb)
# and the soil moisture files have been downloaded, this script will load satellite soil moisture data into the database
#
# Required files:
# - soil moisture data: https://www.esa.int/Applications/Observing_the_Earth/Space_for_our_climate/Nearly_four_decades_of_soil_moisture_data_now_available
#
# Output:
# - soil_moisture: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#soil_moisture
# -------------------------------------------
from dotenv import load_dotenv
import geopandas as gpd  # type: ignore
import xarray as xr  # type: ignore
import sqlalchemy as sq
import pandas as pd
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService
from SoilMoistureQueryHandler import SoilMoistureQueryHandler  # type: ignore


TABLE = "soil_moisture"  # The table used to store the moisture data
AG_REGIONS_TABLE = "census_ag_regions"  # The table that holds the agriculture regions

MAIN_FOLDER_PATH = "data/common/Images/"  # Main folder that contains the moisture files
LOG_FILE = "data/pull_moisture.log"  # The file used to store progress information
ERROR_FILE = "data/pull_moisture.err"  # The file used to store ERROR information


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


def main():
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        updateLog(LOG_FILE, "Missing database credentials")
        raise ValueError("Environment variables not set")

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    conn = db.connect()

    # Check if the soil moisture table exists, if not create it
    queryHandler = SoilMoistureQueryHandler()
    queryHandler.createSoilMoistureTableReq(db)

    # Load the agriculture regions
    agRegions = loadGeometry(conn)

    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        folders = os.listdir(MAIN_FOLDER_PATH)
    except:
        updateLog(ERROR_FILE, f"[ERROR] could not access {MAIN_FOLDER_PATH}")
        sys.exit()

    numErrors = 0  # Used to keep track of how many files are added to the database

    for folder in folders:
        try:
            folderPath = os.path.join(MAIN_FOLDER_PATH, folder)
            updateLog(LOG_FILE, f"Started Updating data for {folder} in {TABLE} ...")

            fileList = get_nc_file_list(folderPath)

            for file in fileList:
                try:
                    os.chdir(os.path.dirname(os.path.abspath(__file__)))
                except:
                    pass

                # Construct the full file path to get the netCDF files
                filePath = os.path.join(folderPath, file)

                # Process then store the moisture data
                df = readNetCDF(filePath)
                df = formatData(df)
                df = addRegions(df, agRegions)
                df.to_sql(TABLE, conn, schema="public", if_exists="append", index=False)

        except Exception as e:
            numErrors += 1
            updateLog(
                ERROR_FILE,
                f"""
                [Error] occurred while listing files in the main folder path: {MAIN_FOLDER_PATH}
                {e}
                """,
            )

    updateLog(
        LOG_FILE,
        f"[SUCCESS] loaded {len(folder_names) - numErrors}/{len(folder_names)} data from {folder_name} into {TABLE}",
    )


def updateLog(fileName: str, message: str) -> None:
    """
    Purpose:
    Outputs progress updates to log files and to the console

    Pseudocode:
    - Check if a filename is provided
    - Opens the file and adds the progress message
    - Print the message to the console
    """
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        if fileName is not None:
            with open(fileName, "a") as log:
                log.write(message + "\n")
    except Exception as e:
        pass


def get_nc_file_list(folder_path: str) -> list:
    """
    Purpose:
    Retrieves a list of netCDF files from a folder

    Pseudocode:
    - [Get a list of files in the folder](https://www.geeksforgeeks.org/python-os-listdir-method/)
    - Pick only the files that end with .nc
    """
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except:
        pass

    file_list = os.listdir(folder_path)  # Get a list of files in the folder
    nc_file_list = [filename for filename in file_list if filename.endswith(".nc")]

    return nc_file_list


def loadGeometry(conn: sq.engine.Connection) -> gpd.GeoDataFrame:
    """
    Purpose:
    Load the [regions](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#census_ag_regions) from the database

    Pseudocode:
    - Create the region SQL query
    - [Load the regions directly into a GeoDataFrame](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.from_postgis.html)
        - crs sets the coordinate system, in our case we want EPSG:3347
        - geom_col specifies which column holds the geometry/boundaries
    """
    query = sq.text(f"select cr_num, district, geometry FROM public.{AG_REGIONS_TABLE}")

    agRegions = gpd.GeoDataFrame.from_postgis(
        query, conn, crs="EPSG:3347", geom_col="geometry"
    )

    return agRegions


def readNetCDF(file: str) -> pd.DataFrame:
    """
    Purpose:
    Reads a netCDF file

    Pseudocode:
    - [Open the file](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html)
    - [Convert its contents into a DataFrame](https://docs.xarray.dev/en/latest/generated/xarray.DataArray.to_dataframe.html)
    - Close the file
    - If an error is encountered, log it
    """
    try:
        dataset = xr.open_dataset(file)
        df = dataset.to_dataframe().reset_index()
        dataset.close()
    except Exception as e:
        updateLog(ERROR_FILE, f"Error reading netCDF file {e}\n")

    return df


def formatData(df: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose:
    Prepares the DataFrame for future processing

    Preprocessing:
    - [Drop irrelevant columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html)
    - Drop irrelevant data
    - [Rename DataFrame columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html)
    """
    df.drop(
        columns=[
            "flag",
            "freqbandID",
            "dnflag",
            "mode",
            "sensor",
            "t0",
            "sm_uncertainty",
        ],
        inplace=True,
    )

    df = df[df["soil_moisture"].notna()]

    df.rename(columns={df.columns[0]: "date"}, inplace=True)
    df.rename(columns={df.columns[3]: "soil_moisture"}, inplace=True)

    return df


def addRegions(df: pd.DataFrame, agRegions: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Purpose:
    Labels the soil moisture data with the agriculture region districts

    Psuedocode:
    - [Create geometry for each set of longitude/latitude](https://geopandas.org/en/stable/docs/reference/api/geopandas.points_from_xy.html) for the data found in the soil moisture data
    - [Set the coordinate system](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html) to the same one used throughout the codebase (EPSG:3347)
    - Label the data to the regions [by joining them together](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html)
        - how=left specifies that the moisture data is always kept even if it does not fall within a region
        - predicate=within joins the data based on which rows of moisture data fall into what regions
    - [Drop irrelevant columns](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html)
    - [Drop irregular data](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.notna.html)
    - [Cast cr_num to an integer](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html)
    """
    df = gpd.GeoDataFrame(
        df, crs="EPSG:4326", geometry=gpd.points_from_xy(df.lon, df.lat)
    )

    # Changes the points projection to match the agriculture regions of EPSG:3347
    df.to_crs(crs="EPSG:3347", inplace=True)  # type: ignore

    # Join the two dataframes based on which points fit within what agriculture regions
    df = gpd.sjoin(df, agRegions, how="left", predicate="within")

    df = pd.DataFrame(df.drop(columns=["index_right", "geometry"]))

    df = df[df["cr_num"].notna()]  # Take rows that are valid numbers
    df[["cr_num"]] = df[["cr_num"]].astype(int)

    return df


if __name__ == "__main__":
    main()
