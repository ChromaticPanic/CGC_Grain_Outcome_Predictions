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


class First15Yrs:
    def __init__(self):
        sq.text()

        self.df = pd.read_sql(weatherDataQuery, conn)
        print()