from ScraperQueries import ScraperQueries
from DataService import DataService
from DataHandler import DataHandler
from datetime import datetime
import sys, os, geopandas, pandas

# add names for tables here
PROVINCES = ['AB', 'SK', 'MB']
PROVINCE_NAMES = ['ALBERTA', 'SAS', 'MANITOBA']
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')


def main():
    db = DataService(PG_DB, PG_USER, PG_PW)
    queryBuilder = ScraperQueries()
    dataHandler = DataHandler()
    requester = cdr()

    conn = db.connect()
    checkTables(db, queryBuilder)

    for prov in PROVINCES:
        query = queryBuilder.getStationsReq(prov)
        stations = geopandas.GeoDataFrame.from_postgis(query, conn, geom_col='geometry')
        df = pandas.DataFrame()
        numUpdated = 0

        for index, row in stations.iterrows():     
            stationID = str(row['Climate ID'])
            query = queryBuilder.getLastUpdatedReq(stationID)
            lastUpdated = db.execute(query)[0]

            # make something to check when ---- needs to be updated
            currYear = min(row['DLY Last Year'], datetime.now().year)
            prevYear = max(row['DLY First Year'], lastUpdated)

            print(f'Pulling data for station {stationID} between {prevYear}-{currYear} ...')
            try:
                df = requester.get_data(prov, stationID, prevYear, currYear)
                        
                if df:
                    df = dataHandler.processData(df, stationID)
                    dataHandler.pushData(df, prov, conn)
                    storeLastUpdated(stationID, queryBuilder)
                    numUpdated += 1
                else:
                    raise Exception('data could not be retrieved')

            except Exception as e:
                print(f'[ERROR] Failed to scrape station {stationID} for {prevYear}-{currYear}')
                print(e)

    print(f'[SUCCESS] Updated the data for {numUpdated}/{len(stations)} weather stations in {prov}')
    db.cleanup()


def checkTables(db, queryBuilder):
    # check if the weather station table exist in the database - if not exit
    query = queryBuilder.tableExistsReq('weather_stations')
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

    # check if the provincial weather station data tables exists in the database - if not create them
    for prov in PROVINCES:
        tablename = f'{prov.lower()}_station_data'
        query = queryBuilder.tableExistsReq(tablename)
        results = db.execute(query)

        if not results[0]:
            query = queryBuilder.createDataTableReq()
            db.execute(query)

def storeLastUpdated(stationID, queryBuilder):
    if lastUpdated:
        query = queryBuilder.modLastUpdatedReq(stationID)
        db.execute(query)
    else:
        query = queryBuilder.addLastUpdatedReq(stationID)
        db.execute(query)


if __name__ == "__main__":
    main()