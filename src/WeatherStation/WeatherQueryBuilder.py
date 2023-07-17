# ----------------------------------------------------
# QueryHandler.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------
import sys, numpy, typing, sqlalchemy

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder


class WeatherQueryBuilder(GenericQueryBuilder):
    def getStationsReq(self, prov: str, stationType: str) -> str:
        return f"""
        SELECT * FROM public.stations_{stationType}
        WHERE province = \'{prov}\' AND {stationType}_first_year IS NOT NULL;
        """

    def getLastUpdatedReq(self, stationID: str) -> str:
        return f"""
        SELECT last_updated, is_active FROM public.station_data_last_updated
        WHERE station_id = \'{stationID}\';
        """

    def readGetLastUpdated(self, results: object) -> typing.Tuple[str, bool]:
        if hasattr(results, "first"):
            row = results.first()
            if row:
                return (str(row[0]), bool(row[1]))
        return ("", False)

    def createHrlyProvStationTableReq(self, tablename: str) -> str:
        # transformed.columns = ['station_id', 'year', 'month', 'day', 'min_temp', 'max_temp', 'mean_temp', 'min_dew_point_temp', 'max_dew_point_temp', 'mean_dew_point_temp', 'min_humidex', 'max_humidex', 'mean_humidex', 'total_precip', 'min_rel_humid', 'max_rel_humid', 'mean_rel_humid', 'min_stn_press', 'max_stn_press', 'mean_stn_press', 'min_visibility', 'max_visibility', 'mean_visibility']
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
        return f"""
        UPDATE station_data_last_updated
        SET last_updated = \'{lastUpdated}\' 
        WHERE station_id = \'{stationID}\';
        COMMIT;
        """

    def addLastUpdatedReq(self, stationID: str, lastUpdated: numpy.datetime64) -> str:
        return f"""
        INSERT INTO station_data_last_updated VALUES (\'{stationID}\', \'{lastUpdated}\');
        COMMIT;
        """
