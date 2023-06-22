# ---------------------------------------------
# To run script the data folder inside of ImportGeo
# Those files are shp and the supporting dbf, prj, and shx files
# These files should correspond to both the province geographical data and the agriculture regions
# Run this script, when viewing in PGAdmin, limit results to prevent the container from crashing
# ---------------------------------------------
import geopandas, sqlalchemy, os
from dotenv import load_dotenv


load_dotenv()
os.environ["USE_PYGEOS"] = "0"

dbURL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PW')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
engine = sqlalchemy.create_engine(dbURL)
conn = engine.connect()

provincesDBF = geopandas.read_file("./data/provinces.shp")
agRegionsDBF = geopandas.read_file("./data/agRegions.shp")

provincesDBF = provincesDBF.set_crs(4617, allow_override=True)
provincesDBF.to_postgis("province", conn, index=False, if_exists="replace")

agRegionsDBF = agRegionsDBF.set_crs(4617, allow_override=True)
provincesDBF.to_postgis("agriculture_region", conn, index=False, if_exists="replace")
conn.commit()
conn.close()
engine.dispose()
