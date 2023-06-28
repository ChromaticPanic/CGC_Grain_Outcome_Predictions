import sys
import sqlalchemy as sq
import os

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService


class SoilMoistureQueryHandler(GenericQueryBuilder):
    def createSoilMoistureTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("soil_moisture"))
        tableExists = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                """
                CREATE TABLE soil_moisture (
                    id              SERIAL,
                    lon             FLOAT,
                    lat             FLOAT,
                    date            DATE,
                    cr_num          INT,
                    car_uid         INT,
                    soil_moisture   FLOAT,
                    CONSTRAINT PK_SOIL_MOISTURE PRIMARY KEY(id)
                );
                COMMIT;
                """
            )

            db.execute(query)
