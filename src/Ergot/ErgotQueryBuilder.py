# ----------------------------------------------------
# QueryHandler.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------

# ----------------------------------------------------
# Purpose:
#         Manually creates the SQL tables to store the soil moisture Data

#         Table:
#         - [ergot_sample](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#ergot_sample)

#         Pseudocode:
#         - Check if the table already exists
#         - If it does not exist, create it

#         Remarks: Creating the table manually ensures the tables persist (usually due to the inability to locate a unique key)
# ----------------------------------------------------

import sys

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder


class ErgotQueryBuilder(GenericQueryBuilder):
    def createErgotSampleTableReq(self) -> str:
        return f"""
        CREATE TABLE ergot_sample (
            sample_id       SERIAL,
            year            INT,
            province        VARCHAR,
            crop_district   INT,
            incidence       BOOL,
            severity        FLOAT,

            CONSTRAINT PK_ERGOT_SAMPLE PRIMARY KEY(sample_id)
        );
        COMMIT;
        """
