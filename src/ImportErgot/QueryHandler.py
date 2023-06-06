# ----------------------------------------------------
# QueryHandler.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------
import os

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
    def createErgotSampleTableReq() -> str:
        return f"""
        CREATE TABLE ergot_sample (
            sample_id       SERIAL,
            year            INT
            province        VARCHAR
            crop_district   INT,
            incidence       BOOL,
            severity        FLOAT,

            CONSTRAINT PK_ERGOT_SAMPLE PRIMARY KEY(sample_id)
        );
        COMMIT;
        """