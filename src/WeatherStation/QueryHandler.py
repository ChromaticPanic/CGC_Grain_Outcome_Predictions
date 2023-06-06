# ----------------------------------------------------
# QueryHandler.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------
import sys, numpy, typing, sqlalchemy

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
    def getStationsReq(self, prov: str) -> str:
        return f"""
        SELECT * FROM public.stations_dly
        WHERE province = \'{prov}\' AND dly_first_year IS NOT NULL;
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