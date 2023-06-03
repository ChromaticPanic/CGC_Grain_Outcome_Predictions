from ClimateDataRequester import ClimateDataRequester
from ScraperQueries import ScraperQueries
from DataService import DataService
from DataHandler import DataHandler
from datetime import datetime
import sys, os, geopandas, pandas

# add names for tables here
PROVINCES = ['AB', 'SK', 'MB']
PROVINCE_NAMES = ['ALBERTA', 'SASKATCHEWAN', 'MANITOBA']

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
        stations = getStations(prov, db, queryBuilder)
        numUpdated = 0

        for index, row in stations.iterrows():     
            stationID = str(row['Climate ID'])
            lastUpdated = row['Last Updated']

            currYear = min(row['DLY Last Year'], datetime.now().year)   # retrieve newest data (unless the station is closed)
            prevYear = max(row['DLY First Year'], lastUpdated)          # start retreiving data from (unless the station did not exist)

            print(f'Pulling data for station {stationID} between {prevYear}-{currYear} ...')
            try:
                df = requester.get_data(prov, stationID, prevYear, currYear)    # gather data       
                df = dataHandler.processData(df, stationID, lastUpdated)        # prepare data for storage
                dataHandler.pushData(df, prov, conn)                            # store data
                storeLastUpdated(stationID, lastUpdated, queryBuilder)          # store date of newest data
                numUpdated += 1
            except Exception as e:
                print(f'[ERROR] Failed to scrape data for station {stationID}')
                print(e)

    print(f'[SUCCESS] Updated the data for {numUpdated} weather stations in {prov}')
    db.cleanup()


def checkTables(db, queryBuilder):
    # check if the weather station table exist in the database - if not exit
    query = queryBuilder.tableExistsReq('weather_station')
    results = db.execute(query)
    if not results[0]:
        print('[ERROR] weather stations have not been loaded into the database yet')
        db.cleanup()
        sys.exit()

    # check if the weather stations last updated table exists in the database - if not create it
    query = queryBuilder.tableExistsReq('station_data_last_updated')
    results = db.execute(query)
    if not results[0]:
        query = queryBuilder.createUpdateTableReq()
        db.execute(query)

def storeLastUpdated(stationID, lastUpdated, queryBuilder):
    if lastUpdated:
        query = queryBuilder.modLastUpdatedReq(stationID, lastUpdated)
        db.execute(query)
    else:
        query = queryBuilder.addLastUpdatedReq(stationID, lastUpdated)
        db.execute(query)

def getStations(prov, db, queryBuilder):
    query = queryBuilder.getStationsReq(prov)
    stations = geopandas.GeoDataFrame.from_postgis(query, conn, geom_col='geometry')
    activeStations = pandas.DataFrame()
    lastUpdated = []

    for index, row in stations.iterrows(): 
        stationID = row['Climate ID']
        query = queryBuilder.getLastUpdatedReq(stationID)
        
        for result in db.execute(query):    # 0: lastUpdated, 1: isActive    
            if(result[1]):
                activeStations.append(stations[('Cliamte ID' == stationID)])
                lastUpdated.append(result[0])

            activeStations['Last Updated'] = lastUpdated

    return stations


if __name__ == "__main__":
    main()