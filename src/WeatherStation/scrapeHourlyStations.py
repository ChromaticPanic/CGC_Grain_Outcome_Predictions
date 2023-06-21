from ClimateDataRequester import ClimateDataRequester
from QueryHandler import QueryHandler
from DataProcessor import DataProcessor
from dotenv import load_dotenv
import os, sys, typing, sqlalchemy 
import numpy as np
import pandas as pd
import geopandas as gpd

sys.path.append('../')
from DataService import DataService


PROVINCES = ['AB', 'SK', 'MB']                      # The abbreviations of the provinces we would like to pull data from
HLY_STATIONS_TABLE = 'stations_hly'                 # Where we collect our stations from (needed to scrape data successfully)

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')
PG_PORT = os.getenv('POSTGRES_PORT')


def main():
    db = DataService(PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW)   # Handles connections to the database
    requester = ClimateDataRequester()                          # Handles weather station requests
    queryHandler = QueryHandler()                               # Handles (builds/processes) requests to the database
    processor = DataProcessor()                                 # Handles the more complex data processing

    conn = db.connect()                     # Connect to the database
    checkTables(db, queryHandler)           # Checks if the tables needed are present, if not try to build them

    for prov in PROVINCES:
        stations = getStations(prov, db, queryHandler, conn)         
        tablename = f'{prov.lower()}_hly_station_data'  
        numUpdated = 0

        query = sqlalchemy.text(queryHandler.tableExistsReq(tablename))
        tableExists = queryHandler.readTableExists(db.execute(query))
        if not tableExists:
            query = sqlalchemy.text(queryHandler.createHrlyProvStationTableReq(tablename))
            db.execute(query)

        print(f'Updating data for {prov} in {tablename} ...')
        for index, row in stations.iterrows():
            startYear = int(row["hly_first_year"])
            endYear = int(row["hly_last_year"])
            stationID = str(row['station_id'])

            print(f'\t[{index + 1}/{len(stations)}] Pulling data for station {stationID} between {startYear}-{endYear}')

            try:
                df = requester.get_hourly_data(stationID, startYear, endYear)      # Collect data from the weather stations for [minYear, maxYear]      
                df = processor.dataProcessHourly(df)             # Prepare data for storage (manipulates dataframe, averages values and removes old data)
                df.to_sql(tablename, conn, schema='public', if_exists="append", index=False)    # Store data (not using return value due to its inaccuracy)
                numRows = len(df.index)                                                         # Check how many rows were in the dataframe we just pushed

                print(f'\t\tupdated {numRows} rows')
                numUpdated += 1
            except Exception as e:
                print(f'[ERROR] Failed to scrape data for station {stationID}')
                print(e)

        print(f'[SUCCESS] Updated data for {numUpdated}/{len(stations)} weather stations in {prov}\n')
    db.cleanup()


def checkTables(db: DataService, queryHandler: QueryHandler):
    # check if the daily weather station table exists in the database - if not exit
    query = sqlalchemy.text(queryHandler.tableExistsReq(HLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))
    if not tableExists:
        print('[ERROR] weather stations have not been loaded into the database yet')
        db.cleanup()
        sys.exit()

def getStations(prov: str, db: DataService, queryHandler: QueryHandler, conn: sqlalchemy.engine.Connection) -> typing.Tuple[pd.DataFrame, list]:
    query = sqlalchemy.text(queryHandler.getStationsReq(prov, 'hly'))
    stations = gpd.GeoDataFrame.from_postgis(query, conn, geom_col='geometry')

    return stations


if __name__ == "__main__":
    main()