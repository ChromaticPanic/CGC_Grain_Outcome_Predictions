# -------------------------------------------
# scrapeDaily.py
#
# After loading the daily weather stations data the following class can be used to scrape the daily weather station data
#   daily weather stations: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/WeatherStation/Data_step%20csv%20import%20geo%20boundaries%20stations.ipynb
#
# Output table:
#   ab_dly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_dly_station_data
#   mb_dly_station_data: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_dly_station_data
#   sk_dly_station_data https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_dly_station_data
#   station_data_last_updated: https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated
# -------------------------------------------
from ClimateDataRequester import ClimateDataRequester  # type: ignore
from WeatherQueryBuilder import WeatherQueryBuilder  # type: ignore
from scrapingProcessor import ScrapingProcessor  # type: ignore
from dotenv import load_dotenv
import geopandas as gpd  # type: ignore
import sqlalchemy as sq
import pandas as pd
import numpy as np
import os, sys, typing

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService


DLY_FLAG = "dly"  # implies we would would like to pull dly station data

# The abbreviations of the provinces we would like to pull data from
PROVINCES = [
    "AB",
    "SK",
    "MB",
]

# The SQL table where the daily stations are located
DLY_STATIONS_TABLE = "stations_dly"

STATIONS_UPDATE_TABLE = "station_data_last_updated"  # The SQL table where we store when a station was last updated


try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

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

    requester = ClimateDataRequester()  # Handles weather station requests
    processor = ScrapingProcessor()  # Handles the more complex data processing
    conn = db.connect()  # Connect to the database

    checkTables(db, queryHandler)

    for prov in PROVINCES:
        stations, states = getStations(prov, db, queryHandler, conn)
        tablename = f"{prov.lower()}_dly_station_data"  # Current province data table
        numUpdated = 0  # Number of records updated

        # Removes inactive stations and adds the date the station was last updated
        stations = processor.removeInactive(stations, states)
        stations = processor.addLastUpdated(stations, states)

        print(f"Updating data for {prov} in {tablename} ...")
        for index, row in stations.iterrows():
            stationID = str(row["station_id"])

            minYear, maxYear = processor.calcDateRange(
                row["dly_first_year"], row["last_updated"], row["dly_last_year"]
            )

            print(
                f"\t[{index + 1}/{len(stations)}] Pulling data for station {stationID} between {int(minYear)}-{int(maxYear)}"
            )

            try:
                # Collect data from the weather stations for [minYear, maxYear]
                df = requester.get_data(prov, stationID, minYear, maxYear)
                # Prepare data for storage (manipulates dataframe, averages values and removes old data)
                df = processor.processData(df, row["last_updated"])
                # Store data (not using return value due to its inaccuracy)
                df.to_sql(
                    tablename, conn, schema="public", if_exists="append", index=False
                )

                # Check what the date was for the newest data point and store it
                updatdUntil = processor.findLatestDate(df["date"])
                if updatdUntil != None:
                    storeLastUpdated(
                        stationID, row["last_updated"], queryHandler, db, updatdUntil
                    )

                print(f"\t\tupdated {len(df.index)} rows")
                numUpdated += 1
            except Exception as e:
                print(f"[ERROR] Failed to scrape data for station {stationID}")
                print(e)

        print(
            f"[SUCCESS] Updated data for {numUpdated}/{len(stations)} weather stations in {prov}\n"
        )
    db.cleanup()


def checkTables(db: DataService, queryHandler: WeatherQueryBuilder):
    """
    Purpose:
    Checks if the necessary tables exist, if not, and if possible they are created. Otherwise the script exits.

    Tables:
    - [stations_dly](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_dly)
    - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

    Pseudocode:
    - Create the query to check if the daily stations are loaded into the database
    - Abort if they are not
    - Check if the update stations table is created
    - If the tables does not exist, create it
    """
    query = sq.text(queryHandler.tableExistsReq(DLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))  # type: ignore
    if not tableExists:
        print("[ERROR] weather stations have not been loaded into the database yet")
        db.cleanup()
        sys.exit()

    # check if the weather stations last updated table exists in the database - if not create it
    query = sq.text(queryHandler.tableExistsReq(STATIONS_UPDATE_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))  # type: ignore
    if not tableExists:
        query = sq.text(queryHandler.createUpdateTableReq())
        db.execute(query)


def storeLastUpdated(
    stationID: str,
    lastUpdated: np.datetime64,
    queryHandler: WeatherQueryBuilder,
    db: DataService,
    updatdUntil: np.datetime64,
):
    """
    Purpose:
    Stores the date a station was last updated

    Tables:
    - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

    Pseudocode:
    - Check if lastUpdated is a valid date (np.datetime64)
    - Adds the station and the date it was last pulled if it was not (this would imply that this is its first update)
    - Updates the date of the last update if it was
    """
    if np.isnat(np.datetime64(lastUpdated)):
        # If it wasnt pulled from, but has been now, add it
        query = sq.text(queryHandler.addLastUpdatedReq(stationID, updatdUntil))
        db.execute(query)
    else:  # Otherwise, modify the date of the last update
        query = sq.text(queryHandler.modLastUpdatedReq(stationID, updatdUntil))
        db.execute(query)


def getStations(
    prov: str,
    db: DataService,
    queryHandler: WeatherQueryBuilder,
    conn: sq.engine.Connection,
) -> typing.Tuple[pd.DataFrame, list]:
    """
    Purpose:
    Gets the daily stations as well as the metadata on when they were last updated

    Tables:
    - [stations_dly](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_dly)
    - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

    Pseudocode:
    - Create the SQL query for the dly weather stations
    - [Load the data from the database directly into a geoDataFrame](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.from_postgis.html)
    - Convert the geoDataFrame into a regular DataFrame without its geometry
    - For each row, check when the station was last updated
    - For each row, add that information into a parallel array

    Remarks:
    Note that stations and states are parallel to one another and that the returned values are as follows:
    - stations is the data from stations_dly without its geometry
    - states is a list of dictionaries containing the station_id (str), last_updated (str) and is_active (bool)
    """
    query = sq.text(queryHandler.getStationsReq(prov, DLY_FLAG))
    stations = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="geometry")
    stations = pd.DataFrame(stations.drop(columns=["geometry"]))
    states = []

    # For each station check if its active and whether or not its been pulled from before (table: station_data_last_updated)
    for index, row in stations.iterrows():
        query = sq.text(queryHandler.getLastUpdatedReq(row["station_id"]))
        lastUpdated, isActive = queryHandler.readGetLastUpdated(db.execute(query))  # type: ignore

        if lastUpdated:
            lastUpdated = str(np.datetime64(lastUpdated))
            states.append(
                {
                    "station_id": row["station_id"],
                    "last_updated": lastUpdated,
                    "is_active": isActive,
                }
            )

    return stations, states


if __name__ == "__main__":
    main()
