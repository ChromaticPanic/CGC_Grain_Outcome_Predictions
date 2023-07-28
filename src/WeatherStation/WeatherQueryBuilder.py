# ----------------------------------------------------
# weatherQueryBuilder.py
#
# Purpose: handles (builds/processes) requests to a database related to the Weather Stations
# ----------------------------------------------------
import sys, numpy, typing

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder


class WeatherQueryBuilder(GenericQueryBuilder):
    def getStationsReq(self, prov: str, stationType: str) -> str:
        """
        Purpose:
        Creates the SQL query to load weather stations (unexecuted)

        Tables:
        - [dly stations](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_dly)
        - [hly stations](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#stations_hly)

        Remarks:
        - Province is an abbreviation
        - Valid stationTypes are dly or hly
        - Stations must have a valid first_year (i.e not null)
        """
        return f"""
        SELECT * FROM public.stations_{stationType}
        WHERE province = \'{prov}\' AND {stationType}_first_year IS NOT NULL;
        """

    def getLastUpdatedReq(self, stationID: str) -> str:
        """
        Purpose:
        Request the date (YEAR-MO-DA) a station was last updated

        Tables:
        - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)
        """
        return f"""
        SELECT last_updated, is_active FROM public.station_data_last_updated
        WHERE station_id = \'{stationID}\';
        """

    def readGetLastUpdated(self, results: object) -> typing.Tuple[str, bool]:
        """
        Purpose:
        Read the results from our request for the date (YEAR-MO-DA) a station was last updated (from getLastUpdatedReq)

        Tables:
        - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

        Pseudocode:
        - Check if the query was successful
        - Load the query results if if they were infact successful, we expect the following results:
            - the date (YEAR-MO-DA) as a string
            - if the station is still active as a boolean
        - Return the results if they were found
        - Return ("", False) if the station has never been updated (and thus no results were returned from station_data_last_updated)
        """
        if hasattr(results, "first"):
            # Contains the date (string) and active flag (boolean) corresponding to a weather station
            # Defaults to the expectation the station has never been updated before
            lastUpdated: typing.Tuple[str, bool] = (
                "",
                False,
            )
            row = results.first()

            if row:  # If we got results, read and return this instead
                lastUpdated = (str(row[0]), bool(row[1]))

        return lastUpdated

    def createHrlyProvStationTableReq(self, tablename: str) -> str:
        """
        Purpose:
        Manually creates the SQL tables to store the hourly weather station data

        Tables:
        - [ab_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ab_hly_station_data)
        - [mb_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#mb_hly_station_data)
        - [sk_hly_station_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#sk_hly_station_data)

        Remarks: Creating the table manually ensures the tables persist (usually due to the inability to locate a unique key)
        """
        return f"""
        CREATE TABLE {tablename} (
            id              SERIAL,
            station_id      VARCHAR,
            year            INT,
            month           INT,
            day             INT,
            min_temp        FLOAT,
            max_temp        FLOAT,
            mean_temp       FLOAT,
            min_dew_point_temp FLOAT,
            max_dew_point_temp FLOAT,
            mean_dew_point_temp FLOAT,
            min_humidex     FLOAT,
            max_humidex     FLOAT,
            mean_humidex    FLOAT,
            total_precip    FLOAT,
            min_rel_humid   FLOAT,
            max_rel_humid   FLOAT,
            mean_rel_humid  FLOAT,
            min_stn_press   FLOAT,
            max_stn_press   FLOAT,
            mean_stn_press  FLOAT,
            min_visibility  FLOAT,
            max_visibility  FLOAT,
            mean_visibility FLOAT,

            CONSTRAINT PK_{tablename.upper()} PRIMARY KEY(id)
        );
        COMMIT;
        """

    def createUpdateTableReq(self):
        """
        Purpose:        
        Manually creates the SQL table to store the metadata for weather stations
        - date (string) and is active flag (boolean)

        Table:
        - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

        Remarks: Creating the table manually ensures the tables persist (usually due to the inability to locate a unique key)
        """
        return f"""
        CREATE TABLE station_data_last_updated (
            station_id      VARCHAR,
            last_updated    DATE NOT NULL,
            is_active       BOOL DEFAULT TRUE,

            CONSTRAINT PK_STATION_UPDATE PRIMARY KEY(station_id)
        );
        COMMIT;
        """

    def modLastUpdatedReq(self, stationID: str, lastUpdated: numpy.datetime64) -> str:
        """
        Purpose:        
        Changes the recorded date a station was last updated

        Table:
        - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

        Remarks:
        This function is used when the station has already been queried before
        """
        return f"""
        UPDATE station_data_last_updated
        SET last_updated = \'{lastUpdated}\' 
        WHERE station_id = \'{stationID}\';
        COMMIT;
        """

    def addLastUpdatedReq(self, stationID: str, lastUpdated: numpy.datetime64) -> str:
        """
        Purpose:        
        Adds the recorded date a station was last updated

        Table:
        - [station_data_last_updated](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#station_data_last_updated)

        Remarks:
        This function is used when the station has never been queried before
        """
        return f"""
        INSERT INTO station_data_last_updated VALUES (\'{stationID}\', \'{lastUpdated}\');
        COMMIT;
        """
