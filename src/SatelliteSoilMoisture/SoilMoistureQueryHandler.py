# ----------------------------------------------------
# SoilMoistureQueryHandler.py
#
# Purpose: handles (builds/processes) requests to a database related to the Soil Moisture
# ----------------------------------------------------
import sqlalchemy as sq
import os, sys

sys.path.append("../")
from Shared.DataService import DataService
from Shared.GenericQueryBuilder import GenericQueryBuilder


# Table name that stores the soil moisture data
SOIL_MOISTURE_TABLE = "soil_moisture"


class SoilMoistureQueryHandler(GenericQueryBuilder):
    def createSoilMoistureTableReq(self, db: DataService):
        """
        Purpose:
        Manually creates the SQL tables to store the soil moisture data

        Table:
        - [soil_moisture](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#soil_moisture)

        Pseudocode:
        - Check if the table already exists
        - If it does not exist, create it

        Remarks: Creating the table manually ensures the tables persist (usually due to the inability to locate a unique key)
        """
        query = sq.text(super().tableExistsReq(SOIL_MOISTURE_TABLE))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                f"""
                CREATE TABLE {SOIL_MOISTURE_TABLE} (
                    id              SERIAL,
                    lon             FLOAT,
                    lat             FLOAT,
                    date            DATE,
                    cr_num          INT,
                    district        INT,
                    soil_moisture   FLOAT,

                    CONSTRAINT PK_SOIL_MOISTURE PRIMARY KEY(id)
                );
                COMMIT;
                """
            )

            db.execute(query)
