from time import sleep
from ClimateDataRequester import ClimateDataRequester  # type: ignore
from WeatherQueryBuilder import WeatherQueryBuilder  # type: ignore
from DataProcessor import DataProcessor  # type: ignore
from dotenv import load_dotenv
import os, sys, typing
import sqlalchemy as sqa
import numpy as np
import pandas as pd
import geopandas as gpd  # type: ignore
import multiprocessing as mp

sys.path.append("../")
from Shared.DataService import DataService


NUM_WORKERS = 12
PROVINCES = [
    "AB",
    "SK",
    "MB",
]  # The abbreviations of the provinces we would like to pull data from
HLY_STATIONS_TABLE = "stations_hly"  # Where we collect our stations from (needed to scrape data successfully)

LOG_FILE = "data/scrape_stations_parallel.log"
ERROR_FILE = "data/scrape_stations_parallel.err"

load_dotenv()
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")


def main():
    db = DataService(
        PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW
    )  # Handles connections to the database
    queryHandler = (
        WeatherQueryBuilder()
    )  # Handles (builds/processes) requests to the database

    conn = db.connect()  # Connect to the database
    checkTables(
        db, queryHandler
    )  # Checks if the tables needed are present, if not try to build them

    for prov in PROVINCES:
        stations = getStations(prov, queryHandler, conn)
        tablename = f"{prov.lower()}_hly_station_data"

        query = sqa.text(queryHandler.tableExistsReq(tablename))
        tableExists = queryHandler.readTableExists(db.execute(query))
        if not tableExists:
            query = sqa.text(queryHandler.createHrlyProvStationTableReq(tablename))
            db.execute(query)

        jobArgs = []
        for index, row in stations.iterrows():
            jobArgs.append(tuple((index, row, len(stations), tablename)))

        updateLog(LOG_FILE, f"Updating data for {prov} in {tablename} ...")
        pool = mp.Pool(NUM_WORKERS)  # Defines the number of workers
        pool.starmap(
            pullHourlyData, jobArgs
        )  # Creates the queue of jobs - pullSateliteData is the function and jobArgs holds the arguments
        pool.close()  # Once these jobs are finished close the multiple processes pool

        updateLog(
            LOG_FILE,
            f"[SUCCESS] Finished updated data for weather stations in {prov}\n",
        )

    db.cleanup()


def pullHourlyData(
    index: int, row: gpd.GeoSeries, numStations: int, tablename: str
) -> None:
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        updateLog(LOG_FILE, "Missing database credentials")
        return
    db = DataService(
        PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW
    )  # Handles connections to the database
    requester = ClimateDataRequester()  # Handles weather station requests
    processor = DataProcessor()  # Handles the more complex data processing
    conn = db.connect()  # Connect to the database

    startYear = int(row["hly_first_year"])
    endYear = int(row["hly_last_year"])
    stationID = str(row["station_id"])

    updateLog(
        LOG_FILE,
        f"\t[{index + 1}/{numStations}] Pulling data for station {stationID} between {startYear}-{endYear}",
    )

    span = endYear - startYear
    for i in range(0, span, 1):
        try:
            # df = requester.get_hourly_data(stationID, startYear, endYear)                 # Collect data from the weather stations for [minYear, maxYear]
            sleep(np.random.randint(5, 20))
            currYear = startYear + i
            df = requester.get_hourly_data(
                stationID, currYear, currYear
            )  # Collect data from the weather stations 1 year at a time
            df = processor.dataProcessHourly(
                df
            )  # Prepare data for storage (manipulates dataframe, averages values and removes old data)
            df = processor.tranformHourlyToDaily(
                df
            )  # Transform hourly data to daily data
            df.to_sql(
                tablename, conn, schema="public", if_exists="append", index=False
            )  # Store data (not using return value due to its inaccuracy)
            numRows = len(
                df.index
            )  # Check how many rows were in the dataframe we just pushed
            updateLog(
                LOG_FILE, f"station {stationID} year {currYear} updated {numRows} rows"
            )

        except Exception as e:
            updateLog(
                ERROR_FILE,
                f"\t\t[ERROR] Failed to scrape data for station {stationID} year {currYear}",
            )
            updateLog(ERROR_FILE, f"\t\t{e}")

    db.cleanup()


def checkTables(db: DataService, queryHandler: WeatherQueryBuilder) -> None:
    # check if the daily weather station table exists in the database - if not exit
    query = sqa.text(queryHandler.tableExistsReq(HLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))  # type: ignore
    if not tableExists:
        updateLog(
            LOG_FILE,
            "[ERROR] weather stations have not been loaded into the database yet",
        )
        db.cleanup()
        sys.exit()


def getStations(
    prov: str, queryHandler: WeatherQueryBuilder, conn: sqa.engine.Connection
) -> gpd.GeoDataFrame:
    query = sqa.text(queryHandler.getStationsReq(prov, "hly"))
    stations = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="geometry")

    return stations


def updateLog(fileName: str, message: str) -> None:
    if fileName is not None:
        with open(fileName, "a") as log:
            log.write(message + "\n")
            log.close()
    else:
        print(message)


if __name__ == "__main__":
    main()
