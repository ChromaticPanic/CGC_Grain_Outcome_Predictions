import sqlalchemy as sq
import geopandas as gpd  # type: ignore
import pandas as pd  # type: ignore
from dotenv import load_dotenv
import os, sys

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService


TABLENAME = "agg_ergot_samples"

load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


class ErgotAggregator:
    def __init__(self):
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

        agRegions = self.pullAgRegions(conn)
        ergot = self.pullErgot(conn)

        ergot = self.calcUIDs(ergot)
        neighbors = self.calcNeighbors(agRegions)
        aggErgot = self.createErgotFeatures(ergot, neighbors)

        try:
            results = sq.text(queryBuilder.tableExistsReq(TABLENAME))
            tableExists = queryBuilder.readTableExists(db.execute(results))

            if not tableExists:
                self.createAggErgotTable(db)

            aggErgot.to_sql(
                TABLENAME, con=conn, schema="public", if_exists="replace", index=False
            )
            conn.commit()
        except Exception as e:
            print([f"[ERROR] {e}"])

        db.cleanup()

    def pullAgRegions(self, conn: sq.engine.Connection) -> gpd.GeoDataFrame:
        regionQuery = sq.text("select district, geometry FROM public.census_ag_regions")

        return gpd.GeoDataFrame.from_postgis(
            regionQuery, conn, crs="EPSG:3347", geom_col="geometry"
        )

    def pullErgot(self, conn: sq.engine.Connection) -> pd.DataFrame:
        ergotQuery = sq.text("SELECT * FROM public.ergot_sample")

        return pd.read_sql_query(ergotQuery, conn)

    def calcUIDs(self, ergot: pd.DataFrame) -> pd.DataFrame:
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

    def calcNeighbors(self, agRegions: gpd.GeoDataFrame) -> dict:
        touches = {}

        for index1, agRegion1 in agRegions.iterrows():
            currTouches = []

            for index2, agRegion2 in agRegions.iterrows():
                if agRegion1["geometry"].touches(agRegion2["geometry"]):
                    currTouches.append(agRegion2["district"])

            touches[str(agRegion1["district"])] = currTouches

        return touches

    def createErgotFeatures(
        self, ergot: pd.DataFrame, touches: gpd.GeoDataFrame
    ) -> pd.DataFrame:
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
                prev1Year = ergot.query(
                    f"year == {year - 1} and district == {district}"
                )
                prev2Year = ergot.query(
                    f"year == {year - 2} and district == {district}"
                )
                prev3Year = ergot.query(
                    f"year == {year - 3} and district == {district}"
                )

                currEntry = {
                    "year": year,
                    "district": district,
                    "percnt_true": currSamples["incidence"].sum() / len(currSamples),
                    "has_ergot": currSamples["incidence"].sum() > 0,
                    "sum_severity": currSamples["severity"].sum(),
                    "present_prev1": prev1Year["incidence"].sum() > 0,
                    "present_prev2": prev2Year["incidence"].sum() > 0,
                    "present_prev3": prev3Year["incidence"].sum() > 0,
                    "present_in_neighbor": neighborSamples["incidence"].sum() > 0,
                    "severity_prev1": prev1Year["incidence"].sum() / len(prev1Year),
                    "severity_prev2": prev2Year["incidence"].sum() / len(prev2Year),
                    "severity_prev3": prev3Year["incidence"].sum() / len(prev3Year),
                    "severity_in_neighbor": neighborSamples["incidence"].sum()
                    / len(neighborSamples),
                }

                ergotList.append(currEntry)

        aggErgot = pd.DataFrame(ergotList)

        # set any unexpected values to 0
        aggErgot.loc[aggErgot["percnt_true"].isna(), "percnt_true"] = 0
        aggErgot.loc[aggErgot["severity_prev1"].isna(), "severity_prev1"] = 0
        aggErgot.loc[aggErgot["severity_prev2"].isna(), "severity_prev2"] = 0
        aggErgot.loc[aggErgot["severity_prev3"].isna(), "severity_prev3"] = 0
        aggErgot.loc[
            aggErgot["severity_in_neighbor"].isna(), "severity_in_neighbor"
        ] = 0

        return aggErgot

    def createAggErgotTable(self, db):
        query = sq.text(
            f"""
            CREATE TABLE {TABLENAME} (
                year                    INT,
                district                INT,
                percnt_true             FLOAT, 
                has_ergot               BOOL, 
                sum_severity            FLOAT, 
                present_prev1           BOOL, 
                present_prev2           BOOL, 
                present_prev3           BOOL, 
                present_in_neighbor     BOOL, 
                severity_prev1          FLOAT, 
                severity_prev2          FLOAT, 
                severity_prev3          FLOAT, 
                severity_in_neighbor    FLOAT,

                CONSTRAINT PK_agg_ergot_sample PRIMARY KEY(year, district)
            );
            COMMIT;
            """
        )

        db.execute(query)
