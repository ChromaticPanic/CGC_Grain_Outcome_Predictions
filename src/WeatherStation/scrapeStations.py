from ClimateDataRequester import ClimateDataRequester
from QueryHandler import QueryHandler
from DataProcessor import DataProcessor
from dotenv import load_dotenv
import sys, os, geopandas, sqlalchemy, numpy, pandas

sys.path.append('../')
from DataService import DataService


# add names for tables here
PROVINCES = ['AB', 'SK', 'MB']
DLY_STATIONS_TABLE = 'stations_dly'
STATIONS_UPDATE_TABLE = 'station_data_last_updated'

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')
PG_PORT = os.getenv('POSTGRES_PORT')


def main():
    db = DataService(PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW) # Handles connections to the database
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
        for index, row in stations.iterrows():      # should include what are the attributes and that this is dataframe
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

        print(f'[SUCCESS] Updated data for {numUpdated}/{len(stations)} weather stations in {prov}\n')
    db.cleanup()


def checkTables(db: DataService, queryHandler: QueryHandler):
    # check if the hourly weather station table exist in the database - if not exit
    query = sqlalchemy.text(queryHandler.tableExistsReq(DLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))
    if not tableExists:
        print('[ERROR] weather stations have not been loaded into the database yet')
        db.cleanup()
        sys.exit()

    # check if the weather stations last updated table exists in the database - if not create it
    query = sqlalchemy.text(queryHandler.tableExistsReq(STATIONS_UPDATE_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))
    if not tableExists:
        query = sqlalchemy.text(queryHandler.createUpdateTableReq())
        db.execute(query)

def storeLastUpdated(stationID: str, lastUpdated: numpy.datetime64, queryHandler: QueryHandler, db: DataService, updatdUntil: numpy.datetime64):
    if numpy.isnat(numpy.datetime64(lastUpdated)):
        query = sqlalchemy.text(queryHandler.addLastUpdatedReq(stationID, updatdUntil))
        db.execute(query)
    else:
        query = sqlalchemy.text(queryHandler.modLastUpdatedReq(stationID, updatdUntil))
        db.execute(query)

def getStations(prov: str, db: DataService, queryHandler: QueryHandler, conn: sqlalchemy.engine.Connection) -> (pandas.DataFrame, [{str, numpy.datetime64, bool}]):
    query = sqlalchemy.text(queryHandler.getStationsReq(prov))
    stations = geopandas.GeoDataFrame.from_postgis(query, conn, geom_col='geometry')
    states = []

    for row in stations:  
        query = sqlalchemy.text(queryHandler.getLastUpdatedReq(row['station_id']))
        lastUpdated, isActive = queryHandler.readGetLastUpdated(db.execute(query))

        if lastUpdated:
            lastUpdated = numpy.datetime64(lastUpdated)
            states.append({'station_id': row['station_id'], 'last_updated': lastUpdated, 'is_active': isActive})

    return stations, states


if __name__ == "__main__":
    main()