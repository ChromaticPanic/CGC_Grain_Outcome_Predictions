import os
import xarray as xr
import geopandas as gpd  # type: ignore

from QueryHandler import QueryHandler
from dotenv import load_dotenv
import sqlalchemy as sq
import sys
import pandas as pd
import matplotlib.pyplot as plt  # type: ignore

sys.path.append("../")
from Shared.DataService import DataService  # type: ignore


TABLE = "agg_soil_moisture"

load_dotenv()
PG_USER = os.getenv("POSTGRES_USER", "")
PG_PW = os.getenv("POSTGRES_PW", "")
PG_DB = os.getenv("POSTGRES_DB", "")
PG_ADDR = os.getenv("POSTGRES_ADDR", "")
PG_PORT = os.getenv("POSTGRES_PORT", 5432)

# connicting to database
db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)
conn = db.connect()

query = sq.text("select * FROM public.soil_moisture")
sm_df = pd.read_sql(query, conn)

# calculating mean by grouping date, cr_num, car_uid
sm_df = (
    sm_df.groupby(["date", "cr_num", "car_uid"])
    .agg({"soil_moisture": ["min", "max", "mean"]})
    .reset_index()
)

# rename columns
sm_df.columns = [  # type: ignore
    "date",
    "cr_num",
    "district",
    "soil_moisture_min",
    "soil_moisture_max",
    "soil_moisture_mean",
]

sm_df[["soil_moisture_min", "soil_moisture_max", "soil_moisture_mean"]] = sm_df[
    ["soil_moisture_min", "soil_moisture_max", "soil_moisture_mean"]
].astype(float)

print(sm_df)

# now push it to database
TABLE = "agg_soil_moisture"
queryHandler = QueryHandler()
queryHandler.createAggSoilMoistureTableReq(db)
sm_df.to_sql(TABLE, conn, schema="public", if_exists="replace")
