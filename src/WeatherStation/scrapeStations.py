from ClimateDataRequester import ClimateDataRequester
from WeatherQueryBuilder import WeatherQueryBuilder
from DataProcessor import DataProcessor
from dotenv import load_dotenv
import os, sys, typing
import sqlalchemy  # type: ignore
import numpy as np
import pandas as pd  # type: ignore
import geopandas as gpd  # type: ignore

sys.path.append("../")
from Shared.DataService import DataService


DLY_FLAG = "dly"
PROVINCES = [
    "AB",
    "SK",
    "MB",
]  # The abbreviations of the provinces we would like to pull data from
DLY_STATIONS_TABLE = "stations_dly"  # Where we collect our stations from (needed to scrape data successfully)
STATIONS_UPDATE_TABLE = "station_data_last_updated"  # The Table where we store when a station was last updated

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
    requester = ClimateDataRequester()  # Handles weather station requests
    queryHandler = (
        WeatherQueryBuilder()
    )  # Handles (builds/processes) requests to the database
    processor = DataProcessor()  # Handles the more complex data processing

    conn = db.connect()  # Connect to the database
    checkTables(
        db, queryHandler
    )  # Checks if the tables needed are present, if not try to build them

    for prov in PROVINCES:
        stations, states = getStations(
            prov, db, queryHandler, conn
        )  # Pulls stations from the datbase. Expected attributes are: station_name, province
        tablename = f"{prov.lower()}_dly_station_data"  # Current province data table   # latitude, longitude, elevation, station_id, wmo_identifier, tc_identifier,
        numUpdated = 0  # Number of records updated     # first_year, last_year, hly_first_year, hly_last_year, dly_first_year, dly_last_year,
        # mly_first_year, mly_last_year, geometry, cr_num, last_updated (gets added in line 38)

        stations = processor.removeInactive(
            stations, states
        )  # Removes inactive stations (as per the datbase)
        stations = processor.addLastUpdated(
            stations, states
        )  # Adds last_updated attribute to the weather stations

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
                df = requester.get_data(
                    prov, stationID, minYear, maxYear
                )  # Collect data from the weather stations for [minYear, maxYear]
                df = processor.processData(
                    df, row["last_updated"]
                )  # Prepare data for storage (manipulates dataframe, averages values and removes old data)
                df.to_sql(
                    tablename, conn, schema="public", if_exists="append", index=False
                )  # Store data (not using return value due to its inaccuracy)
                numRows = len(
                    df.index
                )  # Check how many rows were in the dataframe we just pushed

                print(f"\t\tupdated {numRows} rows")
                if numRows:
                    updatdUntil = processor.findLatestDate(
                        df["date"]
                    )  # Check what the date was for the newest data point
                    storeLastUpdated(
                        stationID, row["last_updated"], queryHandler, db, updatdUntil
                    )  # Store date of newest data (as per line 55)

                numUpdated += 1
            except Exception as e:
                print(f"[ERROR] Failed to scrape data for station {stationID}")
                print(e)

        print(
            f"[SUCCESS] Updated data for {numUpdated}/{len(stations)} weather stations in {prov}\n"
        )
    db.cleanup()


def checkTables(db: DataService, queryHandler: WeatherQueryBuilder):
    # check if the daily weather station table exists in the database - if not exit
    query = sqlalchemy.text(queryHandler.tableExistsReq(DLY_STATIONS_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))  # type: ignore
    if not tableExists:
        print("[ERROR] weather stations have not been loaded into the database yet")
        db.cleanup()
        sys.exit()

    # check if the weather stations last updated table exists in the database - if not create it
    query = sqlalchemy.text(queryHandler.tableExistsReq(STATIONS_UPDATE_TABLE))
    tableExists = queryHandler.readTableExists(db.execute(query))  # type: ignore
    if not tableExists:
        query = sqlalchemy.text(queryHandler.createUpdateTableReq())
        db.execute(query)


def storeLastUpdated(
    stationID: str,
    lastUpdated: np.datetime64,
    queryHandler: WeatherQueryBuilder,
    db: DataService,
    updatdUntil: np.datetime64,
):
    if np.isnat(
        np.datetime64(lastUpdated)
    ):  # lastUpdated is None if its respective station has not had its data pulled yet
        query = sqlalchemy.text(
            queryHandler.addLastUpdatedReq(stationID, updatdUntil)
        )  # If it wasnt pulled from, but has been now, add it
        db.execute(query)
    else:
        query = sqlalchemy.text(
            queryHandler.modLastUpdatedReq(stationID, updatdUntil)
        )  # Otherwise, modify the date of the last update
        db.execute(query)


def getStations(
    prov: str,
    db: DataService,
    queryHandler: WeatherQueryBuilder,
    conn: sqlalchemy.engine.Connection,
) -> typing.Tuple[pd.DataFrame, list]:
    query = sqlalchemy.text(queryHandler.getStationsReq(prov, DLY_FLAG))
    stations = gpd.GeoDataFrame.from_postgis(query, conn, geom_col="geometry")
    states = []

    # For each station check if its active and whether or not its been pulled from before (table: station_data_last_updated)
    for index, row in stations.iterrows():
        query = sqlalchemy.text(queryHandler.getLastUpdatedReq(row["station_id"]))
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
