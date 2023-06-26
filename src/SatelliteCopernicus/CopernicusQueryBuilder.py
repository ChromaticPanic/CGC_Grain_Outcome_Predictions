import sys
import sqlalchemy as sq

sys.path.append("../")
sys.path.append("../Shared")
from GenericQueryBuilder import GenericQueryBuilder  # type: ignore
from DataService import DataService  # type: ignore


class CopernicusQueryBuilder(GenericQueryBuilder):
    def createCopernicusTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("copernicus_satelite_data"))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                """
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
                    car_uid                         INT,
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
            )

            db.execute(query)

    def createCopernicusAggTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("copernicus_satelite_data"))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                """
                CREATE TABLE copernicus_satelite_data (
                    id                              SERIAL,
                    lon                             FLOAT,
                    lat                             FLOAT,
                    datetime                        DATE,
                    year                            INT,
                    month                           INT,
                    day                             INT,
                    cr_num                          INT,
                    car_uid                         INT,
                    dewpoint_temperature_min             FLOAT,
                    temperature_min                      FLOAT,
                    evaporation_from_bare_soil_min       FLOAT,
                    skin_reservoir_content_min           FLOAT,
                    skin_temperature_min                 FLOAT,
                    snowmelt_min                         FLOAT,
                    soil_temperature_level_1_min         FLOAT,
                    soil_temperature_level_2_min         FLOAT,
                    soil_temperature_level_3_min         FLOAT,
                    soil_temperature_level_4_min         FLOAT,
                    surface_net_solar_radiation_min      FLOAT,
                    surface_pressure_min                 FLOAT,
                    volumetric_soil_water_layer_1_min    FLOAT,
                    volumetric_soil_water_layer_2_min    FLOAT,
                    volumetric_soil_water_layer_3_min    FLOAT,
                    volumetric_soil_water_layer_4_min    FLOAT,
                    leaf_area_index_high_vegetation_min  FLOAT,
                    leaf_area_index_low_vegetation_min   FLOAT,

                    dewpoint_temperature_max             FLOAT,
                    temperature_max                      FLOAT,
                    evaporation_from_bare_soil_max       FLOAT,
                    skin_reservoir_content_max           FLOAT,
                    skin_temperature_max                 FLOAT,
                    snowmelt_max                         FLOAT,
                    soil_temperature_level_1_max         FLOAT,
                    soil_temperature_level_2_max         FLOAT,
                    soil_temperature_level_3_max         FLOAT,
                    soil_temperature_level_4_max         FLOAT,
                    surface_net_solar_radiation_max      FLOAT,
                    surface_pressure_max                 FLOAT,
                    volumetric_soil_water_layer_1_max    FLOAT,
                    volumetric_soil_water_layer_2_max    FLOAT,
                    volumetric_soil_water_layer_3_max    FLOAT,
                    volumetric_soil_water_layer_4_max    FLOAT,
                    leaf_area_index_high_vegetation_max  FLOAT,
                    leaf_area_index_low_vegetation_max   FLOAT,
                    
                    dewpoint_temperature_mean            FLOAT,
                    temperature_mean                     FLOAT,
                    evaporation_from_bare_soil_mean      FLOAT,
                    skin_reservoir_content_mean          FLOAT,
                    skin_temperature_mean                FLOAT,
                    snowmelt_mean                        FLOAT,
                    soil_temperature_level_1_mean        FLOAT,
                    soil_temperature_level_2_mean        FLOAT,
                    soil_temperature_level_3_mean        FLOAT,
                    soil_temperature_level_4_mean        FLOAT,
                    surface_net_solar_radiation_mean     FLOAT,
                    surface_pressure_mean                FLOAT,
                    volumetric_soil_water_layer_1_mean   FLOAT,
                    volumetric_soil_water_layer_2_mean   FLOAT,
                    volumetric_soil_water_layer_3_mean   FLOAT,
                    volumetric_soil_water_layer_4_mean   FLOAT,
                    leaf_area_index_high_vegetation_mean FLOAT,
                    leaf_area_index_low_vegetation_mean  FLOAT,
                    
                    CONSTRAINT PK_COPERNICUS PRIMARY KEY(id)
                );
                COMMIT;
                """
            )

            db.execute(query)
