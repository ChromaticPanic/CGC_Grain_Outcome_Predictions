import sys
from typing import Union
import sqlalchemy as sq
import numpy as np

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
    def createCopernicusTableReq(self) -> str:
        return """
        CREATE TABLE copernicus_satelite_data (
            id                              SERIAL,
            lon                             FLOAT,
            lat                             FLOAT,
            datetime                        DATE,
            year                            INT,
            month                           INT,
            day                             INT,
            hour                            INT,
            region                          VARCHAR,
            dewpoint_temperature            FLOAT,
            temperature                     FLOAT,
            evaporation_from_bare_soil      FLOAT,
            skin_reservoir_content          FLOAT,
            skin_temperature                FLOAT,
            snowmelt                        FLOAT,
            soil_temperature_level_1        FLOAT,
            soil_temperature_level_2        FLOAT,
            soil_temperature_level_3        FLOAT,
            soil_temperature_level_4        FLOAT,
            surface_net_solar_radiation     FLOAT,
            surface_pressure                FLOAT,
            volumetric_soil_water_layer_1   FLOAT,
            volumetric_soil_water_layer_2   FLOAT,
            volumetric_soil_water_layer_3   FLOAT,
            volumetric_soil_water_layer_4   FLOAT,
            
            CONSTRAINT PK_COPERNICUS PRIMARY KEY(id)
        );
        COMMIT;
        """

    def createRowExistsInDBReq(self, lon: float, lat: float, datetime: np.datetime64) -> str:
        return f"""
        SELECT EXISTS (
            SELECT FROM public.copernicus_satelite_data
            WHERE lon = {lon} AND lat = {lat} AND datetime = \'{datetime}\'
        );
        """
        
    def readRowExistsInDB(self, results: sq.engine.cursor.CursorResult) -> bool:
        return results.first()[0]

    def createInsertRowReq(self, lon: float, lat: float, datetime: np.datetime64, year: str, month: str, day: str, hour: str, region: str, attr: str, value: Union[float, str]) -> str:
        return f"""
        INSERT INTO public.copernicus_satelite_data (lon, lat, datetime, year, month, day, hour, region, {attr})
        VALUES ({lon}, {lat}, \'{datetime}\', {year}, {month}, {day}, {hour}, \'{region}\', {value});
        COMMIT;
        """

    def createUpdateRowReq(self, lon: float, lat: float, datetime: np.datetime64, attr: str, value: Union[float, str]) -> str:
        return f"""
        UPDATE public.copernicus_satelite_data
        SET {attr} = {value}
        WHERE lon = {lon} AND lat = {lat} AND datetime = \'{datetime}\';
        COMMIT;
        """