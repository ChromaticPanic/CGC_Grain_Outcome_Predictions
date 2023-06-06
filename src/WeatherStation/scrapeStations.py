from ClimateDataRequester import ClimateDataRequester
from QueryHandler import QueryHandler
from DataService import DataService
from DataProcessor import DataProcessor
from datetime import datetime
import sys, os, geopandas, pandas
import sqlalchemy as sq
from dotenv import load_dotenv
import numpy as np

# add names for tables here
PROVINCES = ['AB', 'SK', 'MB']
DLY_STATIONS_TABLE = 'stations_dly'
STATIONS_UPDATE_TABLE = 'station_data_last_updated'

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')


def main():
    db = DataService(PG_DB, PG_USER, PG_PW) # Handles connections to the database
    requester = ClimateDataRequester()      # Handles weather station requests
    queryHandler = QueryHandler()           # Handles (builds/processes) requests to the database
    processor = DataProcessor()             # Handles the more complex data processing

    conn = db.connect()                     # connect to the database
    checkTables(db, queryHandler)           # checks if the tables needed are present, if not try to build them

    for prov in PROVINCES:
        stations, states = getStations(prov, db, queryHandler, conn)
        tablename = f'{prov.lower()}_station_data'
        numUpdated = 0

        stations = processor.removeInactive(stations, states)
        stations = processor.addLastUpdated(stations, states)

        print(f'Updating data for {prov} in {tablename} ...')
        for index, row in stations.iterrows():     
            stationID = str(row['station_id'])
            lastUpdated = row['last_updated']

            minYear, maxYear = processor.calcDateRange(row['dly_first_year'], lastUpdated, row['dly_last_year'])
            print(f'\t[{index + 1}/{len(stations)}] Pulling data for station {stationID} between {int(minYear)}-{int(maxYear)}')

            try:
                df = requester.get_data(prov, stationID, minYear, maxYear)    # gather data       
                df = processor.processData(df, stationID, lastUpdated)        # prepare data for storage
                rowsUpdated = df.to_sql(tablename, conn, schema='public', if_exists="append", index=False)
                print(f'\t\tupdated {rowsUpdated} rows')
                
                if rowsUpdated:
                    updatdUntil = processor.findLatestDate(df['date'])
                    storeLastUpdated(stationID, lastUpdated, queryHandler, db, updatdUntil)      # store date of newest data

                numUpdated += 1
            except Exception as e:
                print(f'[ERROR] Failed to scrape data for station {stationID}')
                print(e)
                sys.exit()

        print(f'[SUCCESS] Updated data for {numUpdated}/{len(stations)} weather stations in {prov}\n')
    db.cleanup()


def checkTables(db: DataService, queryHandler: QueryHandler):
    # check if the hourly weather station table exist in the database - if not exit
    query = sq.text(queryHandler.tableExistsReq(DLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))
    if not tableExists:
        print('[ERROR] weather stations have not been loaded into the database yet')
        db.cleanup()
        sys.exit()

    # check if the weather stations last updated table exists in the database - if not create it
    query = sq.text(queryHandler.tableExistsReq(STATIONS_UPDATE_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))
    if not tableExists:
        query = sq.text(queryHandler.createUpdateTableReq())
        db.execute(query)

def storeLastUpdated(stationID: str, lastUpdated: np.datetime64, queryHandler: QueryHandler, db: DataService, updatdUntil: np.datetime64):
    if np.isnat(np.datetime64(lastUpdated)):
        query = sq.text(queryHandler.addLastUpdatedReq(stationID, updatdUntil))
        db.execute(query)
    else:
        query = sq.text(queryHandler.modLastUpdatedReq(stationID, updatdUntil))
        db.execute(query)

def getStations(prov: str, db: DataService, queryHandler: QueryHandler, conn: sq.engine.Connection) -> (pandas.DataFrame, [{str, numpy.datetime64, bool}]):
    query = sq.text(queryHandler.getStationsReq(prov))
    stations = geopandas.GeoDataFrame.from_postgis(query, conn, geom_col='geometry')
    states = []

    for index, row in stations.iterrows():  
        query = sq.text(queryHandler.getLastUpdatedReq(row['station_id']))
        lastUpdated, isActive = queryHandler.readGetLastUpdated(db.execute(query))

        if lastUpdated:
            lastUpdated = np.datetime64(lastUpdated)
            states.append({'station_id': row['station_id'], 'last_updated': lastUpdated, 'is_active': isActive})

    return stations, states


if __name__ == "__main__":
    main()