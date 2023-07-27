from dotenv import load_dotenv
import geopandas as gpd  # type: ignore
import sqlalchemy as sq
import pandas as pd
import os, sys

sys.path.append("../")
from Shared.DataService import DataService


TABLENAME = "agg_soil_data"
SOIL_GEOM_TABLE = "soil_geometry"
SOIL_COMP_TABLE = "soil_components"
SOIL_SURRONDINGS_TABLE = "soil_surronding_land"
SOIL_DATA_TABLE = "soil_data"

load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


class SoilAggregator:
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
        conn = db.connect()

        # get data
        soil_data = self.pullSoilData(conn)
        surronding_soil = self.pullSurroundingSoil(conn)
        soil_components = self.pullSoilComponents(conn)
        soil_geometry = self.pullSoilGeometry(conn)

        # Merge data and aggregate them
        merge_df = self.getMergedf(
            soil_data, surronding_soil, soil_components, soil_geometry
        )

        # Command to add to db
        merge_df.to_sql(
            TABLENAME, conn, schema="public", if_exists="replace", index=False
        )
        conn.commit()
        db.cleanup()

    def pullSoilData(self, conn: sq.engine.Connection) -> pd.DataFrame:
        query = sq.text("SELECT * FROM public.soil_data")
        soil_data = pd.read_sql(query, conn)
        soil_data = soil_data[
            [
                "id",
                "province",
                "percnt_coarse_frag",
                "total_sand",
                "total_silt",
                "total_clay",
                "percnt_carbon",
                "calcium_ph",
                "proj_ph",
                "water_reten_0",
                "water_reten_10",
                "water_reten_33",
                "water_reten_1500",
                "bulk_density",
                "elec_cond",
                "percnt_wood",
            ]
        ]

        soil_data.rename(columns={"id": "soil_id"}, inplace=True)

        return soil_data

    def pullSurroundingSoil(self, conn: sq.engine.Connection) -> pd.DataFrame:
        query = sq.text("SELECT * FROM public.soil_surronding_land")
        surronding_soil = pd.read_sql(query, conn)
        surronding_soil = surronding_soil[["poly_id", "land_area", "water_area"]]

        return surronding_soil

    def pullSoilComponents(self, conn: sq.engine.Connection) -> pd.DataFrame:
        query = sq.text("SELECT * FROM public.soil_components")
        soil_components = pd.read_sql(query, conn)
        soil_components = soil_components[
            [
                "poly_id",
                "province",
                "percent",
                "soil_id",
                "water_holding_cap",
            ]
        ]

        return soil_components

    def pullSoilGeometry(self, conn: sq.engine.Connection) -> pd.DataFrame:
        # load the boundaries for the agriculture regions
        regionQuery = sq.text("select district, geometry FROM public.census_ag_regions")
        agRegions = gpd.GeoDataFrame.from_postgis(
            regionQuery, conn, crs="EPSG:3347", geom_col="geometry"
        )

        soilQuery = sq.text("select * FROM public.soil_geometry")
        soilRegions = gpd.GeoDataFrame.from_postgis(
            soilQuery, conn, crs="EPSG:3347", geom_col="geometry"
        )

        # Join to add district to df
        soil_geometry = gpd.sjoin(
            soilRegions, agRegions, how="inner", predicate="intersects"
        )
        soil_geometry.drop(columns=["geometry", "index_right"], inplace=True)
        soil_geometry = pd.DataFrame(soil_geometry)

        return soil_geometry

    def getMergedf(
        self,
        soil_data: pd.DataFrame,
        surronding_soil: pd.DataFrame,
        soil_components: pd.DataFrame,
        soil_geometry: pd.DataFrame,
    ) -> pd.DataFrame:
        # Commands to join tables
        merge_df = soil_components.merge(
            soil_data, on=["soil_id", "province"], how="inner"
        )
        merge_df = merge_df.merge(surronding_soil, on="poly_id", how="inner")
        merge_df = merge_df.merge(soil_geometry, on="poly_id", how="inner")

        # Commands to change attributes which are object types
        merge_df["water_holding_cap"] = pd.to_numeric(
            merge_df["water_holding_cap"], errors="coerce"
        )

        # Removes the columns we wont want to scale by weights (percent of polygon occupied)
        cols = merge_df.columns.tolist()
        cols.remove("poly_id")
        cols.remove("province")
        cols.remove("soil_id")
        cols.remove("percent")
        cols.remove("district")

        # Modifies values to take the percentage of attributes into account
        for index in range(len(merge_df)):
            for col in cols:
                merge_df.loc[index, col] = (
                    merge_df.loc[index, "percent"] * merge_df.loc[index, col] * 0.01
                )

        merge_df.drop(
            columns=["poly_id", "province", "soil_id", "percent"], inplace=True
        )

        # Aggregate Data
        final_df = (
            merge_df.groupby(["district"])
            .agg(
                {
                    "percnt_coarse_frag": ["mean"],
                    "total_sand": ["mean"],
                    "total_silt": ["mean"],
                    "total_clay": ["mean"],
                    "percnt_carbon": ["mean"],
                    "calcium_ph": ["mean"],
                    "proj_ph": ["mean"],
                    "water_reten_0": ["mean"],
                    "water_reten_10": ["mean"],
                    "water_reten_33": ["mean"],
                    "water_reten_1500": ["mean"],
                    "bulk_density": ["mean"],
                    "elec_cond": ["mean"],
                    "percnt_wood": ["mean"],
                    "water_holding_cap": ["mean"],
                    "land_area": ["mean"],
                    "water_area": ["mean"],
                }
            )
            .reset_index()
        )

        # rename columns
        final_df.columns = [  # type: ignore
            "district",
            "avg_percnt_coarse_frag",
            "avg_total_sand",
            "avg_total_silt",
            "avg_total_clay",
            "avg_percnt_carbon",
            "avg_calcium_ph",
            "avg_proj_ph",
            "avg_water_reten_0",
            "avg_water_reten_10",
            "avg_water_reten_33",
            "avg_water_reten_1500",
            "avg_bulk_density",
            "avg_elec_cond",
            "avg_percnt_wood",
            "avg_water_holding_cap",
            "avg_land_area",
            "avg_water_area",
        ]

        return final_df
