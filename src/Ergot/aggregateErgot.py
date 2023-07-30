# -------------------------------------------
# aggregateErgot.py
#
# The purpose of this code is to perform data transformation and aggregation to create the two versions of the aggregated table with different sets of features.
#
# Output:
# [agg_ergot_sample](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_ergot_sample)
#
# Remarks: null values - na.mask, null etc... can sometimes cause issues
# -------------------------------------------

# %%
from dotenv import load_dotenv
import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import pandas as pd
import numpy as np
import os, sys

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService

# %%
TABLENAME = "agg_ergot_sample"  # Table name that stores the aggregated ergot data
TABLENAMEV2 = "agg_ergot_sample_v2"  # Table name that stores the aggregated ergot data with different features.
ERGOT_DOWNGRADE_THRESHOLD = 0.04

# Load the database connection environment variables
load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


# %%
# Purpose:
# - The purpose of this function is to fetch the agricultural region data from the PostgreSQL database and convert it into a GeoDataFrame
def pullAgRegions(conn: sq.engine.Connection) -> gpd.GeoDataFrame:
    regionQuery = sq.text("select district, geometry FROM public.census_ag_regions")

    return gpd.GeoDataFrame.from_postgis(
        regionQuery, conn, crs="EPSG:3347", geom_col="geometry"
    )


# %%
# Purpose : Self contained data retrieval data aggregation
# Psuedocode:
# - Create the ergot data SQL query and load it into a Pandas DataFrame.
# - [Load the data from the database directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)


def pullErgot(conn: sq.engine.Connection) -> pd.DataFrame:
    ergotQuery = sq.text("SELECT * FROM public.ergot_sample")

    return pd.read_sql_query(ergotQuery, conn)


# %%

# Purpose:
# - The purpose of this function is to calculate and assign unique identifiers (UIDs) to each row in the ergot DataFrame based on the combination of "province" and "crop_district" values.


def calcUIDs(ergot: pd.DataFrame) -> pd.DataFrame:
    ergot.loc[ergot["province"] == "MB", "district"] = (
        ergot.loc[ergot["province"] == "MB", "crop_district"] + 4600
    )
    ergot.loc[ergot["province"] == "SK", "district"] = (
        ergot.loc[ergot["province"] == "SK", "crop_district"] - 1
    ) + 4700
    ergot.loc[ergot["province"] == "AB", "district"] = (
        ergot.loc[ergot["province"] == "AB", "crop_district"] * 10
    ) + 4800

    ergot[["district"]] = ergot[["district"]].astype(int)

    return ergot


# %%

# Purpose:
# - The purpose of this function is to calculate the neighboring agricultural regions for each region in the agRegions GeoDataFrame based on their geometries.


def calcNeighbors(agRegions: gpd.GeoDataFrame) -> dict:
    touches = {}

    for index1, agRegion1 in agRegions.iterrows():
        currTouches = []

        for index2, agRegion2 in agRegions.iterrows():
            if agRegion1["geometry"].touches(agRegion2["geometry"]):
                currTouches.append(agRegion2["district"])

        touches[str(agRegion1["district"])] = currTouches

    return touches


# %%

# Purpose:
# - The purpose of this function is to aggregate and calculate various features for each unique combination of "year" and "district" in the input ergot DataFrame.
# Psuedocode :
# - This function calculates and assigns unique identifiers (UIDs) to each row in the input Pandas DataFrame.
# - The UIDs are based on the combination of "province" and "crop_district" values.
# - converts the "district" column to integer data type.
# - Load the current samples for the current "year" and "district" for each unique year and district.
# - Convert the "ergotList" into a Pandas DataFrame.
# - Create bins for "ergot_present" and "sum_severity" features based on the Interquartile Range (IQR).


def createErgotFeatures(ergot: pd.DataFrame, touches: gpd.GeoDataFrame) -> pd.DataFrame:
    ergotList = []

    for year in ergot["year"].unique():
        for district in ergot["district"].unique():
            # load the current ag_region samples
            currSamples = ergot.query(f"year == {year} and district == {district}")

            # load the neighbors samples
            neighborSamples = ergot.query(
                f"year == {year} and district in {touches[str(district)]}"
            )

            # load samples for some of the previous years
            prev1Year = ergot.query(f"year == {year - 1} and district == {district}")
            prev2Year = ergot.query(f"year == {year - 2} and district == {district}")
            prev3Year = ergot.query(f"year == {year - 3} and district == {district}")

            currEntry = {
                "year": year,
                "district": district,
                "percnt_true": currSamples["incidence"].sum() / len(currSamples),
                "has_ergot": currSamples["incidence"].sum() > 0,
                "median_severity": currSamples["severity"].median(),
                "sum_severity": currSamples["severity"].sum(),
                "present_in_neighbor": neighborSamples["incidence"].sum() > 0,
                "sum_severity_in_neighbor": neighborSamples["incidence"].sum()
                / len(neighborSamples),
                "present_prev1": prev1Year["incidence"].sum() > 0,
                "present_prev2": prev2Year["incidence"].sum() > 0,
                "present_prev3": prev3Year["incidence"].sum() > 0,
                "sum_severity_prev1": prev1Year["incidence"].sum() / len(prev1Year),
                "sum_severity_prev2": prev2Year["incidence"].sum() / len(prev2Year),
                "sum_severity_prev3": prev3Year["incidence"].sum() / len(prev3Year),
                "percnt_true_prev1": prev1Year["incidence"].sum() / len(prev1Year),
                "percnt_true_prev2": prev2Year["incidence"].sum() / len(prev2Year),
                "percnt_true_prev3": prev3Year["incidence"].sum() / len(prev3Year),
                "median_prev1": prev1Year["severity"].median(),
                "median_prev2": prev2Year["severity"].median(),
                "median_prev3": prev3Year["severity"].median(),
            }

            ergotList.append(currEntry)

    aggErgot = pd.DataFrame(ergotList)

    # set any unexpected values to 0
    aggErgot.loc[aggErgot["percnt_true"].isna(), "percnt_true"] = 0
    aggErgot.loc[aggErgot["sum_severity_prev1"].isna(), "severity_prev1"] = 0
    aggErgot.loc[aggErgot["sum_severity_prev2"].isna(), "severity_prev2"] = 0
    aggErgot.loc[aggErgot["sum_severity_prev3"].isna(), "severity_prev3"] = 0
    aggErgot.loc[
        aggErgot["sum_severity_in_neighbor"].isna(), "severity_in_neighbor"
    ] = 0

    # bin ergot_present and sum_severity by IQR
    q1_ergot_present_cutoff = np.percentile(aggErgot.percnt_true, 25)
    q2_ergot_present_cutoff = np.percentile(aggErgot.percnt_true, 50)
    q3_ergot_present_cutoff = np.percentile(aggErgot.percnt_true, 75)

    q1_sum_severity_severity_cutoff = np.percentile(aggErgot.sum_severity, 25)
    q2_sum_severity_severity_cutoff = np.percentile(aggErgot.sum_severity, 50)
    q3_sum_severity_severity_cutoff = np.percentile(aggErgot.sum_severity, 75)

    aggErgot["ergot_present_in_q1"] = False
    aggErgot["ergot_present_in_q2"] = False
    aggErgot["ergot_present_in_q3"] = False
    aggErgot["ergot_present_in_q4"] = False

    aggErgot["sum_severity_in_q1"] = False
    aggErgot["sum_severity_in_q2"] = False
    aggErgot["sum_severity_in_q3"] = False
    aggErgot["sum_severity_in_q4"] = False

    aggErgot.loc[
        aggErgot["percnt_true"] <= q1_ergot_present_cutoff, "ergot_present_in_q1"
    ] = True
    aggErgot.loc[
        (aggErgot["percnt_true"] > q1_ergot_present_cutoff)
        & (aggErgot["percnt_true"] <= q2_ergot_present_cutoff),
        "ergot_present_in_q2",
    ] = True
    aggErgot.loc[
        (aggErgot["percnt_true"] > q2_ergot_present_cutoff)
        & (aggErgot["percnt_true"] <= q3_ergot_present_cutoff),
        "ergot_present_in_q3",
    ] = True
    aggErgot.loc[
        aggErgot["percnt_true"] > q3_ergot_present_cutoff, "ergot_present_in_q4"
    ] = True

    aggErgot.loc[
        aggErgot["sum_severity"] <= q1_sum_severity_severity_cutoff,
        "sum_severity_in_q1",
    ] = True
    aggErgot.loc[
        (aggErgot["sum_severity"] > q1_ergot_present_cutoff)
        & (aggErgot["sum_severity"] <= q2_ergot_present_cutoff),
        "sum_severity_in_q2",
    ] = True
    aggErgot.loc[
        (aggErgot["sum_severity"] > q2_ergot_present_cutoff)
        & (aggErgot["sum_severity"] <= q3_ergot_present_cutoff),
        "sum_severity_in_q3",
    ] = True
    aggErgot.loc[
        aggErgot["sum_severity"] > q3_sum_severity_severity_cutoff,
        "sum_severity_in_q4",
    ] = True

    return aggErgot


# %%

# Purpose :
# - This function calculates and aggregates features for each unique combination of "year" and "district" in the input Pandas DataFrame.
# Psuedocode :
# - Load the samples for neighboring districts based on the "touches" information.
# - Load samples for some of the previous years (year - 1, year - 2, year - 3) for the current "district".
# - Calculate various aggregated features for the current combination of "year" and "district," such as:
#     - Percentage of true values (incidence) for the current samples.
#     - Presence of ergot in the current samples based on the severity sum and ERGOT_DOWNGRADE_THRESHOLD.
#     - Median and sum of severity for the current samples.
#     - Presence of ergot in neighboring districts based on the severity sum and ERGOT_DOWNGRADE_THRESHOLD.
#     - Various statistics for samples from previous years (presence, median, sum of severity).
# - Append the calculated features to a dictionary named "currEntry".
# - Append the "currEntry" dictionary to the "ergotList".


def createErgotFeaturesV2(
    ergotdf: pd.DataFrame, touches: gpd.GeoDataFrame
) -> pd.DataFrame:
    ergotList = []

    for year in ergotdf["year"].unique():
        for district in ergotdf["district"].unique():
            # load the current ag_region samples
            currSamples = ergotdf.query(f"year == {year} and district == {district}")

            # load the neighbors samples
            neighborSamples = ergotdf.query(
                f"year == {year} and district in {touches[str(district)]}"
            )

            # load samples for some of the previous years
            prev1Year = ergotdf.query(f"year == {year - 1} and district == {district}")
            prev2Year = ergotdf.query(f"year == {year - 2} and district == {district}")
            prev3Year = ergotdf.query(f"year == {year - 3} and district == {district}")

            currEntry = {
                "year": year,
                "district": district,
                "percnt_true": currSamples["incidence"].sum() / len(currSamples),
                "has_ergot": currSamples["severity"].sum() > ERGOT_DOWNGRADE_THRESHOLD,
                "median_severity": currSamples["severity"].median(),
                "sum_severity": currSamples["severity"].sum(),
                "present_in_neighbor": neighborSamples["severity"].sum()
                > ERGOT_DOWNGRADE_THRESHOLD,
                "sum_severity_in_neighbor": neighborSamples["severity"].sum()
                / len(neighborSamples),
                "present_prev1": prev1Year["severity"].sum()
                > ERGOT_DOWNGRADE_THRESHOLD,
                "present_prev2": prev2Year["severity"].sum()
                > ERGOT_DOWNGRADE_THRESHOLD,
                "present_prev3": prev3Year["severity"].sum()
                > ERGOT_DOWNGRADE_THRESHOLD,
                "sum_severity_prev1": prev1Year["severity"].sum(),
                "sum_severity_prev2": prev2Year["severity"].sum(),
                "sum_severity_prev3": prev3Year["severity"].sum(),
                "percnt_true_prev1": prev1Year["incidence"].sum() / len(prev1Year),
                "percnt_true_prev2": prev2Year["incidence"].sum() / len(prev2Year),
                "percnt_true_prev3": prev3Year["incidence"].sum() / len(prev3Year),
                "median_prev1": prev1Year["severity"].median(),
                "median_prev2": prev2Year["severity"].median(),
                "median_prev3": prev3Year["severity"].median(),
            }

            ergotList.append(currEntry)

    aggErgot = pd.DataFrame(ergotList)

    # set any unexpected values to 0
    aggErgot.loc[aggErgot["percnt_true"].isna(), "percnt_true"] = 0
    aggErgot.loc[aggErgot["sum_severity_prev1"].isna(), "severity_prev1"] = 0
    aggErgot.loc[aggErgot["sum_severity_prev2"].isna(), "severity_prev2"] = 0
    aggErgot.loc[aggErgot["sum_severity_prev3"].isna(), "severity_prev3"] = 0
    aggErgot.loc[
        aggErgot["sum_severity_in_neighbor"].isna(), "severity_in_neighbor"
    ] = 0

    return aggErgot


# %%

# Purpose : Create a respective AggErgotTable from the attributes retrieved from previous calls of functions.


def createAggErgotTable(db):
    query = sq.text(
        f"""
        CREATE TABLE {TABLENAME} (
            year                        INT,
            district                    INT,
            percnt_true                 FLOAT, 
            has_ergot                   BOOL, 
            median_severity             FLOAT,
            sum_severity                FLOAT, 

            present_in_neighbor         BOOL, 
            sum_severity_in_neighbor    FLOAT,

            present_prev1               BOOL, 
            present_prev2               BOOL, 
            present_prev3               BOOL, 
            
            sum_severity_prev1          FLOAT, 
            sum_severity_prev2          FLOAT, 
            sum_severity_prev3          FLOAT, 
            
            percnt_true_prev1           FLOAT,
            percnt_true_prev2           FLOAT,
            percnt_true_prev3           FLOAT,

            median_prev1                FLOAT,
            median_prev2                FLOAT,
            median_prev3                FLOAT,
            
            percnt_true_in_q1           BOOL,
            percnt_true_in_q2           BOOL,
            percnt_true_in_q3           BOOL,
            percnt_true_in_q4           BOOL,     

            sum_severity_in_q1          BOOL,
            sum_severity_in_q2          BOOL,
            sum_severity_in_q3          BOOL,
            sum_severity_in_q4          BOOL,

            CONSTRAINT PK_agg_ergot_sample PRIMARY KEY(year, district)
        );
        COMMIT;
        """
    )

    db.execute(query)


# %%
def createAggErgotTableV2(db):
    query = sq.text(
        f"""
        CREATE TABLE {TABLENAMEV2} (
            year                        INT,
            district                    INT,
            percnt_true                 FLOAT, 
            has_ergot                   BOOL, 
            median_severity             FLOAT,
            sum_severity                FLOAT, 

            present_in_neighbor         BOOL, 
            sum_severity_in_neighbor    FLOAT,

            present_prev1               BOOL, 
            present_prev2               BOOL, 
            present_prev3               BOOL, 
            
            sum_severity_prev1          FLOAT, 
            sum_severity_prev2          FLOAT, 
            sum_severity_prev3          FLOAT, 
            
            percnt_true_prev1           FLOAT,
            percnt_true_prev2           FLOAT,
            percnt_true_prev3           FLOAT,

            median_prev1                FLOAT,
            median_prev2                FLOAT,
            median_prev3                FLOAT,

            CONSTRAINT PK_agg_ergot_sample PRIMARY KEY(year, district)
        );
        COMMIT;
        """
    )

    db.execute(query)


# %%

# Purpose :
# - This function is responsible for aggregating ergot data, creating features, and storing the aggregated data in a new table. The function connects to the database using environment variables for the connection parameters, fetches the required data from the database, calculates various features for the data, and then creates a new table to store the aggregated data.


def createAggErgotV1() -> None:
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        raise ValueError("Environment variables not set")

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    queryBuilder = GenericQueryBuilder()
    conn = db.connect()

    agRegions = pullAgRegions(conn)
    ergot = pullErgot(conn)

    ergot = calcUIDs(ergot)
    neighbors = calcNeighbors(agRegions)
    aggErgot = createErgotFeatures(ergot, neighbors)

    try:
        results = sq.text(queryBuilder.tableExistsReq(TABLENAME))
        tableExists = queryBuilder.readTableExists(db.execute(results))

        if not tableExists:
            createAggErgotTable(db)

        aggErgot.to_sql(
            TABLENAME, con=conn, schema="public", if_exists="replace", index=False
        )
        # conn.commit()
    except Exception as e:
        print([f"[ERROR] {e}"])

    db.cleanup()


# %%
def createAggErgotV2() -> None:
    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        raise ValueError("Environment variables not set")

    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
    queryBuilder = GenericQueryBuilder()
    conn = db.connect()

    agRegions = pullAgRegions(conn)
    ergot = pullErgot(conn)

    ergot = calcUIDs(ergot)
    neighbors = calcNeighbors(agRegions)
    aggErgot = createErgotFeaturesV2(ergot, neighbors)

    try:
        results = sq.text(queryBuilder.tableExistsReq(TABLENAMEV2))
        tableExists = queryBuilder.readTableExists(db.execute(results))

        if not tableExists:
            createAggErgotTableV2(db)

        aggErgot.to_sql(
            TABLENAMEV2, con=conn, schema="public", if_exists="replace", index=False
        )
        # conn.commit()
    except Exception as e:
        print([f"[ERROR] {e}"])

    db.cleanup()


# %%
def main():
    # createAggErgotV1()
    createAggErgotV2()


# %%
if __name__ == "__main__":
    main()
