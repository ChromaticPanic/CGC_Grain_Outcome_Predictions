import os
import xarray as xr
import geopandas as gpd
from QueryHandler import QueryHandler
from dotenv import load_dotenv
import sqlalchemy as sq
import sys

sys.path.append("../")
from DataService import DataService

# change the path to main image folder
main_folder_path = r"C:\jay projects\school\COMP 4560\images"

TABLE = 'soil_moisture'

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')
PG_PORT = os.getenv('POSTGRES_PORT')

queryHandler = QueryHandler()

db = DataService(PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW)
conn = db.connect()

queryHandler.createSoilMoistureTableReq(db)

query = sq.text('select cr_num, geometry FROM public.census_ag_regions')
agRegions = gpd.GeoDataFrame.from_postgis(query, conn, crs='EPSG:3347', geom_col='geometry')

folder_names = os.listdir(main_folder_path)

for folder_name in folder_names:
    folder_path = os.path.join(main_folder_path, folder_name)

    # Get a list of all files in the folder
    file_list = os.listdir(folder_path)

    # Filter the file list to include only NetCDF files
    nc_file_list = [filename for filename in file_list if filename.endswith('.nc')]

    points_in_region = []

    for nc_file in nc_file_list:
        # Construct the full file path
        netcdf_file_path = os.path.join(folder_path, nc_file)

        dataset = xr.open_dataset(netcdf_file_path)
        df = dataset.to_dataframe().reset_index()  # Converts the contents into a dataframe and corrects indexes

        dataset.close()

        df.drop(columns=['flag', 'freqbandID', 'dnflag', 'mode', 'sensor', 't0'], inplace=True)
        df.rename(columns={df.columns[0]: "date"}, inplace=True)
        df.rename(columns={df.columns[3]: "soil_moisture"}, inplace=True)
        df = df[df['soil_moisture'].notna()]

        df = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=gpd.points_from_xy(df.lon,
                                                                               df.lat))  # Creates geometry from df using lon and lat as cords to create points (points being geometry)
        df = df.to_crs(crs='EPSG:3347')  # Changes the points projection to match the agriculture regions of EPSG:3347
        df = gpd.sjoin(df, agRegions, how='left',
                       predicate='within')  # Join the two dataframes based on which points fit within what agriculture regions

        df.drop(columns=['index_right', 'geometry'], inplace=True)
        df = df[df['cr_num'].notna()]  # Take rows that are valid numbers
        df[['cr_num']] = df[['cr_num']].astype(int)

        df = df.reset_index()

        df.drop(columns=['index'], inplace=True)

        df.to_sql(TABLE, conn, schema='public', if_exists="append", index=False)


