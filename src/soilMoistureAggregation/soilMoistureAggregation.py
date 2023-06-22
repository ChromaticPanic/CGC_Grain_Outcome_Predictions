import os
import xarray as xr
import geopandas as gpd
# from QueryHandler import QueryHandler
from dotenv import load_dotenv
import sqlalchemy as sq
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append("../")
from DataService import DataService


load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')
PG_PORT = os.getenv('POSTGRES_PORT')

# connicting to database
db = DataService(PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW)
conn = db.connect()

query = sq.text('select * FROM public.soil_moisture')
sm_df = pd.read_sql(query, conn)

# calculating mean by grouping date, cr_num, car_uid
sm_df = sm_df.groupby(['date', 'cr_num', 'car_uid']).mean().reset_index()

# drop id, lat, lon columns from df
sm_df.drop(columns = ['id', 'lat', 'lon'], inplace=True)

# rename car_uid to district
sm_df.rename(columns = {'car_uid':'district'}, inplace = True)

# now push it to database