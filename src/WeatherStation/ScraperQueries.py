class ScraperQueries:
    def getStationsReq(self, prov):
        return f"""
        SELECT * FROM public.weather_stations
        WHERE province = {prov} AND dly_first_year IS NOT NULL;
        """
        
    def getLastUpdatedReq(self, stationID):
        return f"""
        SELECT year FROM public.station_data_last_updated
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
            station_id  INT,
            year        INT NOT NULL,

        CONSTRAINT PK_STATION_UPDATE PRIMARY KEY (station_id)
        );
        """

    # def createDataTableReq(self, prov):
    #     return f"""
    #     CREATE TABLE {prov}_station_data (
    #         station_id      INT, 
    #         climate_id      INT,
    #         date            VARCHAR,
    #         year            INT,
    #         month           INT,
    #         day             INT,
    #         max_temp        FLOAT,
    #         min_temp        FLOAT,
    #         mean_temp       FLOAT,
    #         total_rain      FLOAT,
    #         total_snow      FLOAT,
    #         total_precip    FLOAT,
    #         snow_on_grnd    FLOAT

    #         CONSTRAINT PK_{prov.upper()}_DATA PRIMARY KEY (station_id, climate_id)
    #     );
    #     """

    def modLastUpdatedReq(stationID, year):
        return f"""
        UPDATE station_data_last_updated
        SET year = {year} 
        WHERE station_id = {stationID};
        """

    def addLastUpdatedReq(stationID, year):        
        return f"""
        INSERT INTO station_data_last_updated VALUES ({stationID}, {year});
        """

    # YYYY-MM-DD