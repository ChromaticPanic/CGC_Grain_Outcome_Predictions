# -------------------------------------------
# scrapeHourlyParallel.py
#
# After loading the hourly weather stations data the following class can be used to scrape the hourly weather station data
#   hourly weather stations: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/WeatherStation/Data_step%20csv%20import%20geo%20boundaries%20stations.ipynb
#
# Output table:
#   ab_hly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_hly_station_data
#   mb_hly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_hly_station_data
#   sk_hly_station_data https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_hly_station_data
#
# Remarks: When tables are updated in the future/the script is ran again, data already pulled may be duplicated
# -------------------------------------------
from ClimateDataRequester import ClimateDataRequester  # type: ignore
from WeatherQueryBuilder import WeatherQueryBuilder  # type: ignore
from scrapingProcessor import ScrapingProcessor  # type: ignore
from dotenv import load_dotenv
from time import sleep
import multiprocessing as mp
import geopandas as gpd  # type: ignore
import sqlalchemy as sq
import numpy as np
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService


NUM_WORKERS = 12  # The number of workers

# The abbreviations of the provinces we would like to pull data from
PROVINCES = [
    "AB",
    "SK",
    "MB",
]

# The SQL table where the hourly stations are located
HLY_STATIONS_TABLE = "stations_hly"

# The file used to store progress information
LOG_FILE = "data/scrape_stations_parallel.log"

# The file used to store error information
ERROR_FILE = "data/scrape_stations_parallel.err"


# Load the database connection environment variables located in the docker folder
load_dotenv("../docker/.env")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")


def main():
    # Handles connections to the database
    db = DataService(PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW)

    # Handles (builds/processes) requests to the database
    queryHandler = WeatherQueryBuilder()

    conn = db.connect()  # Connect to the database
    checkTables(db, queryHandler)

    for prov in PROVINCES:
        stations = getStations(prov, queryHandler, conn)
        tablename = f"{prov.lower()}_hly_station_data"
        jobArgs = []

        # Check if the table exists yet, if not add it
        query = sq.text(queryHandler.tableExistsReq(tablename))
        tableExists = queryHandler.readTableExists(db.execute(query))
        if not tableExists:
            query = sq.text(queryHandler.createHrlyProvStationTableReq(tablename))
            db.execute(query)

        for index, row in stations.iterrows():
            jobArgs.append(tuple((index, row, len(stations), tablename)))

        updateLog(LOG_FILE, f"Updating data for {prov} in {tablename} ...")
        pool = mp.Pool(NUM_WORKERS)  # Defines the number of workers

        # Creates the queue of jobs - pullSateliteData is the function and jobArgs holds the arguments
        pool.starmap(pullHourlyData, jobArgs)
        pool.close()  # Once these jobs are finished close the multiple processes pool

        updateLog(
            LOG_FILE,
            f"[SUCCESS] Finished updated data for weather stations in {prov}\n",
        )

    db.cleanup()


def pullHourlyData(index: int, row: gpd.GeoSeries, numStations: int, tablename: str):
    """
    Purpose:
    Pulls the hourly data and updates the database

    Tables:
    - [ab_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_hly_station_data)
    - [mb_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_hly_station_data)
    - [sk_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_hly_station_data)

    Pseudocode:
    - Connect to the database
    - Update the logs as data starts getting pulled
    - Calculate the time span
    - Start a random delay (to prevent being detected as a bot)
    - Request the data
    - Preprocess the data
    - Store the data
    - Update logs
    - Disconnect from the database

    Remarks: When tables are updated in the future/the script is ran again, data already pulled may be duplicated
    """
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        updateLog(LOG_FILE, "Missing database credentials")
        return

    # Handles connections to the database
    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    conn = db.connect()  # Connect to the database

    requester = ClimateDataRequester()  # Handles weather station requests
    processor = ScrapingProcessor()  # Handles the more complex data processing

    startYear = int(row["hly_first_year"])
    endYear = int(row["hly_last_year"])
    stationID = str(row["station_id"])

    updateLog(
        LOG_FILE,
        f"\t[{index + 1}/{numStations}] Pulling data for station {stationID} between {startYear}-{endYear}",
    )

    span = endYear - startYear
    for i in range(0, span):
        try:
            sleep(np.random.randint(5, 20))
            currYear = startYear + i

            # Collect data from the weather stations 1 year at a time
            df = requester.get_hourly_data(stationID, currYear, currYear)
            # Prepare data for storage (manipulates dataframe, averages values and removes old data)
            df = processor.dataProcessHourly(df)
            # Transform hourly data to daily data
            df = processor.tranformHourlyToDaily(df)

            # Store data (not using return value due to its inaccuracy)
            df.to_sql(tablename, conn, schema="public", if_exists="append", index=False)

            updateLog(
                LOG_FILE,
                f"station {stationID} year {currYear} updated {len(df.index)} rows",
            )

        except Exception as e:
            updateLog(
                ERROR_FILE,
                f"\t\t[ERROR] Failed to scrape data for station {stationID} year {currYear}",
            )
            updateLog(ERROR_FILE, f"\t\t{e}")

    db.cleanup()


def checkTables(db: DataService, queryHandler: WeatherQueryBuilder):
    """
    Purpose:
    Checks if the necessary tables exist, if not, the script exits

    Tables:
    - [stations_hly](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_hly)

    Pseudocode:
    - Create the query to check if the hourly stations are loaded into the database
    - Abort if they are not
    """
    query = sq.text(queryHandler.tableExistsReq(HLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))  # type: ignore
    if not tableExists:
        updateLog(
            LOG_FILE,
            "[ERROR] weather stations have not been loaded into the database yet",
        )
        db.cleanup()
        sys.exit()


def getStations(
    prov: str, queryHandler: WeatherQueryBuilder, conn: sq.engine.Connection
) -> gpd.GeoDataFrame:
    """
    Purpose:
    Gets the hourly stations

    Tables:
    - [stations_hly](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_hly)

    Pseudocode:
    - Create the SQL query for the hly weather stations
    - [Load the data from the database directly into a geoDataFrame](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.from_postgis.html)
    """
    query = sq.text(queryHandler.getStationsReq(prov, "hly"))
    stations = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="geometry")

    return stations


def updateLog(fileName: str, message: str):
    """
    Purpose:
    Outputs progress updates to log files/to the console if no filename is provided

    Pseudocode:
    - Check if a filename is provided
    - Sets the current directory to the files directory if it is
    - Opens the file and adds the progress message
    - Otherwise, print the message
    """
    if fileName is not None:
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        except:
            pass

        with open(fileName, "a") as log:
            log.write(message + "\n")
    else:
        print(message)


if __name__ == "__main__":
    main()
