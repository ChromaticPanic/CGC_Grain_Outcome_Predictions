import sqlalchemy as sq
import sys

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService


class CopernicusQueryBuilder(GenericQueryBuilder):
    def createCopernicusTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("agg_day_copernicus_satellite_data"))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                """
                CREATE TABLE agg_day_copernicus_satellite_data (
                    id                              SERIAL,
                    year                            INT,
                    month                           INT,
                    day                             INT,
                    cr_num                          INT,
                    district                        INT,
                    
                    min_dewpoint_temperature             FLOAT,
                    min_temperature                      FLOAT,
                    min_evaporation_from_bare_soil       FLOAT,
                    min_skin_reservoir_content           FLOAT,
                    min_skin_temperature                 FLOAT,
                    min_snowmelt                         FLOAT,
                    min_soil_temperature_level_1         FLOAT,
                    min_soil_temperature_level_2         FLOAT,
                    min_soil_temperature_level_3         FLOAT,
                    min_soil_temperature_level_4         FLOAT,
                    min_surface_net_solar_radiation      FLOAT,
                    min_surface_pressure                 FLOAT,
                    min_volumetric_soil_water_layer_1    FLOAT,
                    min_volumetric_soil_water_layer_2    FLOAT,
                    min_volumetric_soil_water_layer_3    FLOAT,
                    min_volumetric_soil_water_layer_4    FLOAT,
                    min_leaf_area_index_high_vegetation  FLOAT,
                    min_leaf_area_index_low_vegetation   FLOAT,

                    max_dewpoint_temperature             FLOAT,
                    max_temperature                      FLOAT,
                    max_evaporation_from_bare_soil       FLOAT,
                    max_skin_reservoir_content           FLOAT,
                    max_skin_temperature                 FLOAT,
                    max_snowmelt                         FLOAT,
                    max_soil_temperature_level_1         FLOAT,
                    max_soil_temperature_level_2         FLOAT,
                    max_soil_temperature_level_3         FLOAT,
                    max_soil_temperature_level_4         FLOAT,
                    max_surface_net_solar_radiation      FLOAT,
                    max_surface_pressure                 FLOAT,
                    max_volumetric_soil_water_layer_1    FLOAT,
                    max_volumetric_soil_water_layer_2    FLOAT,
                    max_volumetric_soil_water_layer_3    FLOAT,
                    max_volumetric_soil_water_layer_4    FLOAT,
                    max_leaf_area_index_high_vegetation  FLOAT,
                    max_leaf_area_index_low_vegetation   FLOAT,
                    
                    mean_dewpoint_temperature            FLOAT,
                    mean_temperature                     FLOAT,
                    mean_evaporation_from_bare_soil      FLOAT,
                    mean_skin_reservoir_content          FLOAT,
                    mean_skin_temperature                FLOAT,
                    mean_snowmelt                        FLOAT,
                    mean_soil_temperature_level_1        FLOAT,
                    mean_soil_temperature_level_2        FLOAT,
                    mean_soil_temperature_level_3        FLOAT,
                    mean_soil_temperature_level_4        FLOAT,
                    mean_surface_net_solar_radiation     FLOAT,
                    mean_surface_pressure                FLOAT,
                    mean_volumetric_soil_water_layer_1   FLOAT,
                    mean_volumetric_soil_water_layer_2   FLOAT,
                    mean_volumetric_soil_water_layer_3   FLOAT,
                    mean_volumetric_soil_water_layer_4   FLOAT,
                    mean_leaf_area_index_high_vegetation FLOAT,
                    mean_leaf_area_index_low_vegetation  FLOAT,
                    
                    CONSTRAINT PK_COPERNICUS PRIMARY KEY(id)
                );
                COMMIT;
                """
            )

            db.execute(query)

    def createCopernicusAggTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("copernicus_satellite_data_agg"))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                """
                CREATE TABLE copernicus_satellite_data_agg (
                    id                              SERIAL,
                    lon                             FLOAT,
                    lat                             FLOAT,
                    datetime                        DATE,
                    year                            INT,
                    month                           INT,
                    day                             INT,
                    cr_num                          INT,
                    district                        INT,
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
