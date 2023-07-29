# ----------------------------------------------------
# CopernicusQueryBuilder.py
#
# Purpose: handles (builds/processes) requests to a database related to the Copernicus Satellite
# ----------------------------------------------------
import sqlalchemy as sq
import sys

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService


# Table name that stores the copernicus satellite data
AGG_COPERNICUS_TABLE = "agg_day_copernicus_satellite_data"


class CopernicusQueryBuilder(GenericQueryBuilder):
    def createCopernicusTableReq(self, db: DataService):
        """
        Purpose:
        Manually creates the SQL tables to store the Copernicus Satellite Data

        Table:
        - [agg_day_copernicus_satellite_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_day_copernicus_satellite_data)

        Pseudocode:
        - Check if the table already exists
        - If it does not exist, create it

        Remarks: Creating the table manually ensures the tables persist (usually due to the inability to locate a unique key)
        """
        query = sq.text(super().tableExistsReq(AGG_COPERNICUS_TABLE))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                f"""
                CREATE TABLE {AGG_COPERNICUS_TABLE} (
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
