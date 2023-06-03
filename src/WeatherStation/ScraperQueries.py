class ScraperQueries:
    def getStationsReq(self, prov):
        return f"""
        SELECT * FROM public.weather_stations
        WHERE province = {prov} AND dly_first_year IS NOT NULL;
        """
        
    def getLastUpdatedReq(self, stationID):
        return f"""
        SELECT last_updated, is_active FROM public.station_data_last_updated
        WHERE station_id = {stationID};
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
            station_id      INT,
            last_updated    DATE NOT NULL,
            is_active       BOOL DEFAULT TRUE,

        CONSTRAINT PK_STATION_UPDATE PRIMARY KEY (station_id)
        );
        """

    def modLastUpdatedReq(self, stationID, lastUpdated): 
        return f"""
        UPDATE station_data_last_updated
        SET last_updated = {lastUpdated} 
        WHERE station_id = {stationID};
        """

    def addLastUpdatedReq(self, stationID, lastUpdated):        
        return f"""
        INSERT INTO station_data_last_updated VALUES ({stationID}, {lastUpdated});
        """

    # YYYY-MM-DD