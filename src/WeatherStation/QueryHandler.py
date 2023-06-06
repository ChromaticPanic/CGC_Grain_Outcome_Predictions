import os

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
    def getStationsReq(self, prov):
        return f"""
        SELECT * FROM public.stations_dly
        WHERE province = \'{prov}\' AND dly_first_year IS NOT NULL;
        """

    def getLastUpdatedReq(self, stationID):
        return f"""
        SELECT last_updated, is_active FROM public.station_data_last_updated
        WHERE station_id = \'{stationID}\';
        """
    
    def readGetLastUpdated(self, results):
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

    def modLastUpdatedReq(self, stationID, lastUpdated): 
        return f"""
        UPDATE station_data_last_updated
        SET last_updated = \'{lastUpdated}\' 
        WHERE station_id = \'{stationID}\';
        COMMIT;
        """

    def addLastUpdatedReq(self, stationID, lastUpdated):        
        return f"""
        INSERT INTO station_data_last_updated VALUES (\'{stationID}\', \'{lastUpdated}\');
        COMMIT;
        """