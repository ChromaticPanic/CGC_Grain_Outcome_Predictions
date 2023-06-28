import sys
import sqlalchemy as sq

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService

class QueryHandler(GenericQueryBuilder):
    def createAggSoilMoistureTableReq(self, db: DataService):
        query = sq.text(super().tableExistsReq("agg_soil_moisture"))
        tableExists: bool = super().readTableExists(db.execute(query))  # type: ignore

        if not tableExists:
            query = sq.text(
                """
                CREATE TABLE agg_soil_moisture (
                    id                      SERIAL,
                    year                    INT,
                    month                   INT,
                    day                     INT,
                    cr_num                  INT,
                    district                INT,
                    soil_moisture_min       FLOAT,
                    soil_moisture_max       FLOAT,
                    soil_moisture_mean      FLOAT,
                    CONSTRAINT PK_AGG_SOIL_MOISTURE PRIMARY KEY(id)
                );
                COMMIT;
                """
            )

            db.execute(query)
