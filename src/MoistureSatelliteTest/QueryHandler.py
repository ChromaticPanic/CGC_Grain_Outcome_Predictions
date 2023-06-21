import sys
import sqlalchemy as sq

sys.path.append("../")
# from Querier import Querier
from Querier import Querier
from DataService import DataService


class QueryHandler(Querier):
    def createSoilMoistureTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("soil_moisture"))
        tableExists = super().readTableExists(db.execute(query))

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
