# ----------------------------------------------------
# QueryHandler.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------
import sys, numpy, typing, sqlalchemy

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
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
    
    def readGetLastUpdated(self, results: sqlalchemy.engine.cursor.CursorResult) -> typing.Tuple[str, bool]:
        results = results.first()
        lastUpdated = None
        isActive = None

        if results:
            lastUpdated = results[0]
            isActive = results[1]

        return lastUpdated, isActive

    def createHrlyProvStationTableReq(self, tablename):
        return f"""
        CREATE TABLE {tablename} (
            id              SERIAL,
            station_id      VARCHAR,
            datetime        DATE,
            year            INT,
            month           INT,
            day             INT,
            hour            INT,
            temp            FLOAT,
            dew_point_temp  FLOAT,
            humidex         FLOAT,
            precip_amount   FLOAT,
            rel_humid       FLOAT,
            stn_press       FLOAT,
            visibility      FLOAT,

            CONSTRAINT PK_{tablename.upper()} PRIMARY KEY(id)
        );
        COMMIT;
        """

        df.rename(columns={df.columns[0]: "station_id"}, inplace=True)
        df.rename(columns={df.columns[1]: "datetime"}, inplace=True)
        df.rename(columns={df.columns[2]: "year"}, inplace=True)
        df.rename(columns={df.columns[3]: "month"}, inplace=True)
        df.rename(columns={df.columns[4]: "day"}, inplace=True)
        df.rename(columns={df.columns[5]: "hour"}, inplace=True)
        df.rename(columns={df.columns[6]: "temp"}, inplace=True)
        df.rename(columns={df.columns[7]: "dew_point_temp"}, inplace=True)
        df.rename(columns={df.columns[8]: "humidex"}, inplace=True)
        df.rename(columns={df.columns[9]: "precip_amount"}, inplace=True)
        df.rename(columns={df.columns[10]: "rel_humid"}, inplace=True)
        df.rename(columns={df.columns[11]: "stn_press"}, inplace=True)
        df.rename(columns={df.columns[12]: "visibility"}, inplace=True)

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