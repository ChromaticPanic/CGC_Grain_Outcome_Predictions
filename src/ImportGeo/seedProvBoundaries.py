# for data in output:
#     seedData += "INSERT INTO province (name, boundaries) VALUES(" + data[0] + ", " + data[1] + ");"

# conn = psycopg2.connect(host=os.getenv('localhost'), port=os.getenv('5432'), database=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=os.getenv('POSTGRES_PW'))
# curr = conn.cursor()

# curr.execute(
#     """
#     CREATE TABLE province (
#         ID SERIAL,
#         name VARCHAR(2) NOT NULL,
#         boundaries geography(MULTIPOLYGON) NOT NULL
#     );
#     """ + seedData
# )


import psycopg2, os
from dotenv import load_dotenv
import geopandas as gpd


load_dotenv()

dbURL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PW')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
engine = sq.create_engine(self.dbURL)
conn = engine.connect()

provincesDBF = gpd.read_file('./data/provinces.dbf', encoding='utf-8')
agRegionsDBF = gpd.read_file('./data/agRegions.dbf', encoding='utf-8')

provincesDBF = provincesDBF.set_crs(4617, allow_override=True)
provincesDBF.to_postgis('province', conn, index=False, if_exists='replace')   

agRegionsDBF = agRegionsDBF.set_crs(4617, allow_override=True)
provincesDBF.to_postgis('agriculture_region', conn, index=False, if_exists='replace')  

conn.dispose()