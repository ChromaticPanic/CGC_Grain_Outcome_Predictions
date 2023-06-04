from ClimateDataRequester import ClimateDataRequester
from ScraperQueries import ScraperQueries
from DataService import DataService
from DataHandler import DataHandler
from datetime import datetime
import sys, os, geopandas, pandas
import sqlalchemy as sq
from dotenv import load_dotenv
# add names for tables here
PROVINCES = ['AB', 'SK', 'MB']
PROVINCE_NAMES = ['ALBERTA', 'SASKATCHEWAN', 'MANITOBA']

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')


def main():
    db = DataService(PG_DB, PG_USER, PG_PW) # database adapter
    requester = ClimateDataRequester()      # handles data requests to weather stations
    queryBuilder = ScraperQueries()         # builds SQL requests for the database
    dataHandler = DataHandler()             # prepares station once recieved to be stored in the datbase

    conn = db.connect()                     # holds a connection to the database
    checkTables(db, queryBuilder)           # checks/builds the database tables necessary

    for prov in PROVINCES:
        stations = getStations(prov, db, queryBuilder, conn)
        numUpdated = 0
        exists = True

        for index, row in stations.iterrows():     
            stationID = str(row['Climate ID'])
            lastUpdated = row['Last Updated']

            if lastUpdated.year == 1:
                exists = False

            currYear = min(row['DLY Last Year'], datetime.now().year)   # retrieve newest data (unless the station is closed)
            prevYear = max(row['DLY First Year'], lastUpdated.year)          # start retreiving data from (unless the station did not exist)

            print(f'Pulling data for station {stationID} between {prevYear}-{currYear} ...')
            try:
                df = requester.get_data(prov, stationID, prevYear, currYear)    # gather data       
                df = dataHandler.processData(df, stationID, lastUpdated)        # prepare data for storage
                lastUpdated = dataHandler.pushData(df, prov, conn)                            # store data
                storeLastUpdated(stationID, lastUpdated, queryBuilder, db, exists)      # store date of newest data
                numUpdated += 1

            except Exception as e:
                print(f'[ERROR] Failed to scrape data for station {stationID}')
                print(e)
                sys.exit()

        print(f'[SUCCESS] Updated the data for {numUpdated} weather stations in {prov}')
    db.cleanup()


def checkTables(db, queryBuilder):
    # check if the hourly weather station table exist in the database - if not exit
    query = sq.text(queryBuilder.tableExistsReq('StationsDly'))
    results = db.execute(query)

    if not results.first()[0]:
        print('[ERROR] weather stations have not been loaded into the database yet')
        db.cleanup()
        sys.exit()

    # check if the weather stations last updated table exists in the database - if not create it
    query = sq.text(queryBuilder.tableExistsReq('station_data_last_updated'))
    results = db.execute(query)
    if not results.first()[0]:
        query = sq.text(queryBuilder.createUpdateTableReq())
        db.execute(query)

def storeLastUpdated(stationID, lastUpdated, queryBuilder, db, exists):
    if exists:
        query = sq.text(queryBuilder.modLastUpdatedReq(stationID, lastUpdated))
        db.execute(query)
    else:
        query = sq.text(queryBuilder.addLastUpdatedReq(stationID, lastUpdated))
        db.execute(query)

def getStations(prov, db, queryBuilder, conn):
    if prov == 'MB':
        prov = 'MANITOBA'
    if prov == 'SK':
        prov = 'SASKATCHEWAN'
    if prov == 'AB':
        prov = 'ALBERTA'

    query = sq.text(queryBuilder.getStationsReq(prov))
    stations = geopandas.GeoDataFrame.from_postgis(query, conn, geom_col='geometry')
    activeStations = pandas.DataFrame()
    lastUpdated = []

    for index, row in stations.iterrows(): 
        stationID = row['Climate ID']

        query = sq.text(queryBuilder.getLastUpdatedReq(stationID))
        results = db.execute(query).first()     # 0: lastUpdated, 1: isActive    
        
        if not results or results[1]:
            activeStations = pandas.concat([activeStations, stations[stations['Climate ID'] == stationID]])
            
            if results:
                date = results[0].split('-')
                lastUpdated.append(datetime(date[0], date[1], date[2]))
            else:
                lastUpdated.append(datetime(1,1,1))
    
    activeStations['Last Updated'] = lastUpdated

    return activeStations


if __name__ == "__main__":
    main()