import sys

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
            leaf_area_index_high_vegetation FLOAT,
            leaf_area_index_low_vegetation  FLOAT,
            
            CONSTRAINT PK_COPERNICUS PRIMARY KEY(id)
        );
        COMMIT;
        """