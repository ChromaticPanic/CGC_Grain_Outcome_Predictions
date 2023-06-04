class ScraperQueries:
    def getStationsReq(self, prov):
        return f"""
        SELECT * FROM public.\"StationsDly\"
        WHERE \"Province\" = \'{prov}\' AND \"DLY First Year\" IS NOT NULL;
        """
        
    def getLastUpdatedReq(self, stationID):
        return f"""
        SELECT last_updated, is_active FROM public.station_data_last_updated
        WHERE station_id = \'{stationID}\';
        """
    
    def tableExistsReq(self, tablename):
        return f"""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = \'public\' AND tablename  = \'{tablename}\'
        );
        """

    def createUpdateTableReq(self):
        return f"""
        CREATE TABLE station_data_last_updated (
            station_id      VARCHAR,
            last_updated    DATE NOT NULL,
            is_active       BOOL DEFAULT TRUE,

        CONSTRAINT PK_STATION_UPDATE PRIMARY KEY (station_id)
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

    # YYYY-MM-DD