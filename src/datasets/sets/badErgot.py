from dotenv import load_dotenv
import sqlalchemy as sq
import pandas as pd

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.DataService import DataService


load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")

SOIL_QUERY = sq.text(
    f"""
    SELECT * FROM public.agg_soil_data;
    """
)

MOISTURE_QUERY = sq.text(
    f"""
    SELECT * FROM public.agg_soil_moisture
    WHERE YEAR >= 2002 AND YEAR <= 2017;
    """
)

ERGOT_QUERY = sq.text(
    f"""
    SELECT * FROM public.agg_ergot_sample
    WHERE YEAR >= 2002 AND YEAR <= 2017;
    """
)


class BadErgot:
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

        pandas.read_csv()

        self.daily = pd.read_sql(badErgotQuery, conn)
        self.weekly
        self.monthly

        db.cleanup()