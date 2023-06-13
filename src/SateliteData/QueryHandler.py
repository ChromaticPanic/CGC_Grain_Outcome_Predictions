import sys
from typing import Union
import sqlalchemy as sq
import numpy as np

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
    def createCopernicusTableReq(self) -> str:
        return f"""
        CREATE TABLE copernicus_satelite_data (
            id                              SERIAL,
            lon                             FLOAT,
            lat                             FLOAT,
            datetime                        DATE,
            year                            INT,
            month                           INT,
            day                             INT,
            hour                            INT,
            cr_num                          INT,
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

    def createInsertRowReq(self, data, year, month, day, hour) -> str:
        return f"""
        INSERT INTO public.copernicus_satelite_data (lon, lat, datetime, year, month, day, hour, region, dewpoint_temperature, temperature, evaporation_from_bare_soil, 
        skin_reservoir_content, skin_temperature, snowmelt, soil_temperature_level_1, soil_temperature_level_2, soil_temperature_level_3, soil_temperature_level_4,
        surface_net_solar_radiation, surface_pressure, volumetric_soil_water_layer_1, volumetric_soil_water_layer_2, volumetric_soil_water_layer_3, volumetric_soil_water_layer_1) 
        
        VALUES ({data['longitude']}, {data['latitude']}, \'{data['time']}\', {year}, {month}, {day}, {hour}, \'{data['cr_num']}\', {data['dewpoint_temperature']}, 
        {data['temperature']}, {data['evaporation_from_bare_soil']}, {data['skin_reservoir_content']}, {data['skin_temperature']}, {data['snowmelt']}, 
        {data['soil_temperature_level_1']}, {data['soil_temperature_level_2']}, {data['soil_temperature_level_3']}, {data['soil_temperature_level_4']}, 
        {data['surface_net_solar_radiation']}, {data['surface_pressure']}, {data['volumetric_soil_water_layer_1']}, {data['volumetric_soil_water_layer_2']}, 
        {data['volumetric_soil_water_layer_3']}, {data['volumetric_soil_water_layer_4']});
        COMMIT;
        """