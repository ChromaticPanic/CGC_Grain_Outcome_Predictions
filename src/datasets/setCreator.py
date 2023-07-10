from sets.first15Yrs import First15Yrs
from sets.badErgot import BadErgot
from sets.complete import Complete
from sets.winter import Winter
from sets.spring import Spring
from sets.summer import Summer
from sets.fall import Fall

from dotenv import load_dotenv
import sqlalchemy as sq
import pandas as pd
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService
from Ergot.ergotAggregator import ErgotAggregator
from ImportSoil.soilAggregator import SoilAggregator

LOCAL_FILE_DATASETS_LOC = "./data"

HLY_CSV_BY_DAY_FILE = "agg_hly_by_day.csv"
HLY_CSV_BY_WEEK_FILE = "agg_hly_by_week.csv"
HLY_CSV_BY_MONTH_FILE = "agg_hly_by_month.csv"

MOISTURE_CSV_BY_DAY_FILE = "agg_moisture_by_day.csv"
MOISTURE_CSV_BY_WEEK_FILE = "agg_moisture_by_week.csv"
MOISTURE_CSV_BY_MONTH_FILE = "agg_moisture_by_month.csv"

AGG_SOIL_TABLE = "agg_soil_data"
AGG_ERGOT_TABLE = "agg_ergot_sample"


load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


class SetCreator:
    def __new__(cls): 
        if not hasattr(cls, 'instance'):
            cls.instance = super(SetCreator, cls).__new__(cls)
        return cls.instance

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
        
        # checks if the data that is needed has been aggregated, if not, proceeds to aggregate it
        self.verifySoilIsAggregated(db, queryBuilder)
        self.verifyErgotIsAggregated(db, queryBuilder)
        self.verifyHlyIsAggregated(LOCAL_FILE_DATASETS_LOC)
        self.verifyMoistureIsAggregated(LOCAL_FILE_DATASETS_LOC)

        # pull all data
        # #hlyDF = pd.read_sql(HLY_QUERY, conn)
        # soilDF = pd.read_sql(SOIL_QUERY, conn)
        # #moistureDF = pd.read_sql(MOISTURE_QUERY, conn)
        # ergotDF = pd.read_sql(ERGOT_QUERY, conn)

        db.cleanup()

        self.addFirst15Yrs()
        self.addBadErgot()
        self.addComplete()
        self.addWinter()
        self.addSpring()
        self.addSummer()
        self.addFall()

        self.listOfSets = []


    def verifySoilIsAggregated(self, db, queryBuilder):
        query = sq.text(queryBuilder.tableExistsReq(AGG_SOIL_TABLE))
        tableExists = queryBuilder.readTableExists(db.execute(query))

        if not tableExists:
            SoilAggregator()

    def verifyErgotIsAggregated(self, db, queryBuilder):
        query = sq.text(queryBuilder.tableExistsReq(AGG_ERGOT_TABLE))
        tableExists = queryBuilder.readTableExists(db.execute(query))

        if not tableExists:
            ErgotAggregator()

    def verifyHlyIsAggregated(self, path):
        hasHlyByDay = os.path.isfile(f"{path}/{HLY_CSV_BY_DAY_FILE}")
        hasHlyByWeek = os.path.isfile(f"{path}/{HLY_CSV_BY_WEEK_FILE}")
        hasHlyByMonth = os.path.isfile(f"{path}/{HLY_CSV_BY_MONTH_FILE}")

        if not hasHlyByDay or not hasHlyByWeek or not hasHlyByMonth:
            print()

    def verifyMoistureIsAggregated(self, path):
        hasMoistureByDay = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_DAY_FILE}")
        hasMoistureByWeek = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_WEEK_FILE}")
        hasMoistureByMonth = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_MONTH_FILE}")
        
        if not hasMoistureByDay or not hasMoistureByWeek or not hasMoistureByMonth:
            print()


    def addFirst15Yrs(self):
        first15Yrs = First15Yrs()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # first 15 years by week, soil moisture, soil
        # first 15 years by day, soil moisture, soil, weather

    def addBadErgot(self):
        badErgot = BadErgot()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # year ergot was worst weather by month
        # year ergot was soil
        # year ergot was worst soil moisture

    def addComplete(self):
        complete = Complete()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # all for weather by month
        # add for weather by week
        # all for weather by day

        # all for soil moisture and moisture by month
        # all for soil moisture and moisture by week
        # all for soil moisture and moisture by day

        # all for weather and soil moisture by month
        # all for weather and soil moisture and soil by month
        # add for weather and soil moisture by week
        # add for weather and soil moisture and soil by week
        # all for weather and soil moisture by day
        # all for weather and soil moisture and soil by day

    def addWinter(self):
        winter = Winter()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # only dataset on winter months

    def addSpring(self):
        spring = Spring()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # onl spring months

    def addSummer(self):
        summer = Summer()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # only dataset on summer months

    def addFall(self):
        fall = Fall()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # onl fall months

    def getSets(self):
        return self.listOfSets