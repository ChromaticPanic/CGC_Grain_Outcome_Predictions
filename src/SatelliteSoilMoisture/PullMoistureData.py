import os
import xarray as xr
import geopandas as gpd  # type: ignore
from dotenv import load_dotenv
import sqlalchemy as sq
import sys

sys.path.append("../")
sys.path.append("../Shared/")

from SoilMoistureQueryHandler import SoilMoistureQueryHandler  # type: ignore
from Shared.DataService import DataService  # type: ignore

# path to soil moister data
MAIN_FOLDER_PATH = "/data/common/Images/"
LOG_FILE = "/data/pull_moisture.log"
ERROR_FILE = "/data/pull_moisture.err"

TABLE = "soil_moisture"

load_dotenv()
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")

if (
    PG_DB is None
    or PG_ADDR is None
    or PG_PORT is None
    or PG_USER is None
    or PG_PW is None
):
    # updateLog(LOG_FILE, "Missing database credentials")
    raise ValueError("Environment variables not set")

def main():
    queryHandler = SoilMoistureQueryHandler()

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    conn = db.connect()

    queryHandler.createSoilMoistureTableReq(db)

    query = sq.text("select cr_num, car_uid, geometry FROM public.census_ag_regions")
    agRegions = get_agriculture_regions(conn)
    
    try:
        folder_names = os.listdir(MAIN_FOLDER_PATH)
    except OSError as e:
        updateLog(
            ERROR_FILE, f"\t\tError occurred while listing files in the main folder path: {MAIN_FOLDER_PATH}"
        )
        updateLog(ERROR_FILE, str(e))
        return

    for folder_name in folder_names:
        print("started : " + folder_name)
        updateLog(LOG_FILE, f"Started Updating data for {folder_name} in {TABLE} ...")
        folder_path = os.path.join(MAIN_FOLDER_PATH, folder_name)

        nc_file_list = get_nc_file_list(folder_path)
        
        try:
            for nc_file in nc_file_list:
                # Construct the full file path
                netcdf_file_path = os.path.join(folder_path, nc_file)
                process_netcdf_file(netcdf_file_path, conn, agRegions)               
                
        except FileNotFoundError as e:
            updateLog(
            ERROR_FILE, f"\t\tError occurred while listing files in the NC files: {nc_file}"
             )
            updateLog(ERROR_FILE, f"\t\t{e}")

        updateLog(LOG_FILE, f"Ended Updating data for {folder_name} in {TABLE} ...")
 
def get_nc_file_list(folder_path):
    # Get a list of all files in the folder
    file_list = os.listdir(folder_path)
    # Filter the file list to include only NetCDF files
    nc_file_list = [filename for filename in file_list if filename.endswith(".nc")]
    return nc_file_list        

def get_agriculture_regions(conn):
    query = sq.text("select cr_num, car_uid, geometry FROM public.census_ag_regions")
    agRegions = gpd.GeoDataFrame.from_postgis(query, conn, crs="EPSG:3347", geom_col="geometry")
    return agRegions

def process_netcdf_file(netcdf_file_path, conn, agRegions):
    dataset = xr.open_dataset(netcdf_file_path)
    df = dataset.to_dataframe().reset_index()  # Converts the contents into a dataframe and corrects indexes
    dataset.close()

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
    df.rename(columns={df.columns[0]: "date"}, inplace=True)
    df.rename(columns={df.columns[3]: "soil_moisture"}, inplace=True)
    df = df[df["soil_moisture"].notna()]

    df = gpd.GeoDataFrame( 
        df, crs="EPSG:4326", geometry=gpd.points_from_xy(df.lon, df.lat)
    ) # Creates geometry from df using lon and lat as cords to create points (points being geometry)
    
    df = df.to_crs( # type: ignore
            crs="EPSG:3347") # Changes the points projection to match the agriculture regions of EPSG:3347

    df = gpd.sjoin(
        df, agRegions, how="left", predicate="within") # Join the two dataframes based on which points fit within what agriculture regions
    
    df.drop(columns=["index_right", "geometry"], inplace=True)
    
    df = df[df["cr_num"].notna()] # Take rows that are valid numbers

    df[["cr_num"]] = df[["cr_num"]].astype(int)
    df = df.reset_index()

    df.drop(columns=["index"], inplace=True)

        # df.to_sql(TABLE, conn, schema="public", if_exists="append", index=False)
    
def updateLog(fileName: str, message: str) -> None:
    try:
        if fileName is not None:
            with open(fileName, "a") as log:
                log.write(message + "\n")
    except Exception as e:
        print(message)

if __name__ == "__main__":
    main()

