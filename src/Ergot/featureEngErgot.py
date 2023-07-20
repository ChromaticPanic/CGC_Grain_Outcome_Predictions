# %%
import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os, sys, calendar

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

from aggregateErgot import calcUIDs  # type: ignore

sys.path.append("../")
from Shared.DataService import DataService
from Shared.GenericQueryBuilder import GenericQueryBuilder


# %%
load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")

if (
    PG_DB is None
    or PG_ADDR is None
    or PG_PORT is None
    or PG_USER is None
    or PG_PW is None
):
    raise ValueError("Environment variables not set")


# %%
def pullIndividualErgotSampleData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.ergot_sample
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def pullAggErgotData(conn: sq.engine.Connection) -> pd.DataFrame:
    # pulling weather station data from the database
    weatherDataQuery = sq.text(
        """
        SELECT * FROM public.agg_ergot_sample_v2
        """
    )

    return pd.read_sql(weatherDataQuery, conn)


# %%
def createErgotFeatEngTableV1(db, tablename: str):
    query = sq.text(
        f"""
        CREATE TABLE {tablename} (
            year                        INT,
            province                    VARCHAR(2),
            crop_district               INT,
            incidence                   BOOL,
            severity                    FLOAT,
            district                    INT,
            downgrade                   BOOL,
            severity_bin_quan           INT,
            severity_bin_arb            INT,

            CONSTRAINT PK_{tablename} PRIMARY KEY(year, district)
        );
        COMMIT;
        """
    )

    db.execute(query)


# %%
def calculateDowngradeColumn(df: pd.DataFrame) -> pd.DataFrame:
    DOWNGRADE_THRESHOLD = 0.04
    df["downgrade"] = False
    df.loc[df["severity"] >= DOWNGRADE_THRESHOLD, "downgrade"] = True
    return df


# %%
def calculateSeverityBinQuan(df: pd.DataFrame) -> pd.DataFrame:
    # quantiles only on severities > 0
    df["severity_bin_quan"] = 0
    df.loc[df["severity"] > 0, "severity_bin_quan"] = pd.qcut(
        df.loc[df["severity"] > 0]["severity"], 4, labels=False
    )
    return df


# %%
def calculateSeverityBinArbitrary(df: pd.DataFrame) -> pd.DataFrame:
    df["severity_bin_arb"] = 0
    df.loc[df["severity"] >= 0.02, "severity_bin_arb"] = 1
    df.loc[df["severity"] >= 0.04, "severity_bin_arb"] = 2
    df.loc[df["severity"] >= 0.08, "severity_bin_arb"] = 3
    return df


# %%
def main():
    TABLENAME = "ergot_sample_feat_eng"

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    conn = db.connect()

    ergotDf = pullIndividualErgotSampleData(conn)
    ergotDf = calcUIDs(ergotDf)
    ergotDf = calculateDowngradeColumn(ergotDf)
    ergotDf = calculateSeverityBinQuan(ergotDf)
    ergotDf = calculateSeverityBinArbitrary(ergotDf)

    try:
        queryBuilder = GenericQueryBuilder()
        request = sq.text(queryBuilder.tableExistsReq(TABLENAME))
        tableExists = queryBuilder.readTableExists(db.execute(request))

        if not tableExists:
            createErgotFeatEngTableV1(db)

        ergotDf.to_sql(
            TABLENAME, conn, schema="public", if_exists="append", index=False
        )
    except Exception as e:
        print("An error occurred while writing to the database {}".format(e))
        raise e

    db.cleanup()


# %%
if __name__ == "__main__":
    main()
