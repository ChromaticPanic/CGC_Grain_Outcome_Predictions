from dotenv import load_dotenv
import sqlalchemy as sq
import pandas as pd  # type: ignore
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

from sets.first15Yrs import First15Yrs
from sets.badErgot import BadErgot
from sets.complete import Complete
from sets.winter import Winter
from sets.spring import Spring
from sets.summer import Summer
from sets.fall import Fall

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService
from Ergot.ergotAggregator import ErgotAggregator
from ImportSoil.soilAggregator import SoilAggregator
from WeatherStation.hlyAggregator import HlyAggregator
from SatelliteSoilMoisture.moistureAggregator import MoistureAggregator

LOCAL_FILE_DATASETS_LOC = "./data"

HLY_CSV_BY_DAY = "agg_hly_by_day.csv"
HLY_CSV_BY_WEEK = "agg_hly_by_week.csv"
HLY_CSV_BY_MONTH = "agg_hly_by_month.csv"

MOISTURE_CSV_BY_DAY = "agg_moisture_by_day.csv"
MOISTURE_CSV_BY_WEEK = "agg_moisture_by_week.csv"
MOISTURE_CSV_BY_MONTH = "agg_moisture_by_month.csv"

AGG_SOIL_TABLE = "agg_soil_data"
AGG_ERGOT_TABLE = "agg_ergot_sample"

SOIL_QUERY = sq.text(f"SELECT * FROM {AGG_SOIL_TABLE};")
ERGOT_QUERY = sq.text(f"SELECT * FROM {AGG_ERGOT_TABLE};")

load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


class SetCreator:
    def __new__(cls):
        if not hasattr(cls, "instance"):
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

        # checks if the data that is needed has been aggregated, if not, proceed to aggregate it
        self.verifySoilIsAggregated(db, queryBuilder)
        self.verifyErgotIsAggregated(db, queryBuilder)
        self.verifyHlyIsAggregated(LOCAL_FILE_DATASETS_LOC)
        self.verifyMoistureIsAggregated(LOCAL_FILE_DATASETS_LOC)

        # pull all data
        self.hlyByDayDF = pd.read_csv(f"{LOCAL_FILE_DATASETS_LOC}/{HLY_CSV_BY_DAY}")
        self.hlyByWeekDF = pd.read_csv(f"{LOCAL_FILE_DATASETS_LOC}/{HLY_CSV_BY_WEEK}")
        self.hlyByMonthDF = pd.read_csv(f"{LOCAL_FILE_DATASETS_LOC}/{HLY_CSV_BY_MONTH}")

        self.moistureByDayDF = pd.read_csv(
            f"{LOCAL_FILE_DATASETS_LOC}/{MOISTURE_CSV_BY_DAY}"
        )
        self.moistureByWeekDF = pd.read_csv(
            f"{LOCAL_FILE_DATASETS_LOC}/{MOISTURE_CSV_BY_WEEK}"
        )
        self.moistureByMonthDF = pd.read_csv(
            f"{LOCAL_FILE_DATASETS_LOC}/{MOISTURE_CSV_BY_MONTH}"
        )

        self.soilDF = pd.read_sql(SOIL_QUERY, conn)
        self.ergotDF = pd.read_sql(ERGOT_QUERY, conn)

        db.cleanup()

        # self.addFirst15Yrs(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )
        # self.addBadErgot(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )
        # self.addComplete(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )
        # self.addWinter(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )
        # self.addSpring(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )
        # self.addSummer(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )
        # self.addFall(
        #     hlyByDayDF,
        #     hlyByWeekDF,
        #     hlyByMonthDF,
        #     moistureByDayDF,
        #     moistureByWeekDF,
        #     moistureByMonthDF,
        #     soilDF,
        #     ergotDF,
        # )

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
        hasHlyByDay = os.path.isfile(f"{path}/{HLY_CSV_BY_DAY}")
        hasHlyByWeek = os.path.isfile(f"{path}/{HLY_CSV_BY_WEEK}")
        hasHlyByMonth = os.path.isfile(f"{path}/{HLY_CSV_BY_MONTH}")

        if not hasHlyByDay or not hasHlyByWeek or not hasHlyByMonth:
            hlyAggregator = HlyAggregator()

            try:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
            except:
                pass

            if not hasHlyByDay:
                hlyAggregator.aggregateByDay(path)
            if not hasHlyByWeek:
                hlyAggregator.aggregateByWeek(path)
            if not hasHlyByMonth:
                hlyAggregator.aggregateByMonth(path)

    def verifyMoistureIsAggregated(self, path):
        hasMoistureByDay = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_DAY}")
        hasMoistureByWeek = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_WEEK}")
        hasMoistureByMonth = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_MONTH}")

        if not hasMoistureByDay or not hasMoistureByWeek or not hasMoistureByMonth:
            moistureAggregator = MoistureAggregator()

            try:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
            except:
                pass

            if not hasMoistureByDay:
                moistureAggregator.aggregateByDay(path)
            if not hasMoistureByWeek:
                moistureAggregator.aggregateByWeek(path)
            if not hasMoistureByMonth:
                moistureAggregator.aggregateByMonth(path)

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
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        except:
            pass

        hasHlyByDay = os.path.isfile(f"{path}/{HLY_CSV_BY_DAY}")
        hasHlyByWeek = os.path.isfile(f"{path}/{HLY_CSV_BY_WEEK}")
        hasHlyByMonth = os.path.isfile(f"{path}/{HLY_CSV_BY_MONTH}")

        if not hasHlyByDay or not hasHlyByWeek or not hasHlyByMonth:
            hlyAggregator = HlyAggregator()

            try:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
            except:
                pass

            if not hasHlyByDay:
                hlyAggregator.aggregateByDay(path)
            if not hasHlyByWeek:
                hlyAggregator.aggregateByWeek(path)
            if not hasHlyByMonth:
                hlyAggregator.aggregateByMonth(path)

    def verifyMoistureIsAggregated(self, path):
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        except:
            pass

        hasMoistureByDay = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_DAY}")
        hasMoistureByWeek = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_WEEK}")
        hasMoistureByMonth = os.path.isfile(f"{path}/{MOISTURE_CSV_BY_MONTH}")

        if not hasMoistureByDay or not hasMoistureByWeek or not hasMoistureByMonth:
            moistureAggregator = MoistureAggregator()

            try:
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
            except:
                pass

            if not hasMoistureByDay:
                moistureAggregator.aggregateByDay(path)
            if not hasMoistureByWeek:
                moistureAggregator.aggregateByWeek(path)
            if not hasMoistureByMonth:
                moistureAggregator.aggregateByMonth(path)


    def addFirst15Yrs(self):
        first15Yrs = First15Yrs(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )
        
        # first 15 years by week, soil moisture, soil
        # first 15 years by day, soil moisture, soil, weather

    def addBadErgot(self):
        badErgot = BadErgot(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )

        # year ergot was worst weather by month
        # year ergot was soil
        # year ergot was worst soil moisture

    def addComplete(self):
        complete = Complete(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )

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
        winter = Winter(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )

        # only dataset on winter months

    def addSpring(self):
        spring = Spring(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )

        # onl spring months

    def addSummer(self):
        summer = Summer(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )

        # only dataset on summer months

    def addFall(self):
        fall = Fall(        
            self.hlyByDayDF,
            self.hlyByWeekDF,
            self.hlyByMonthDF,
            self.moistureByDayDF,
            self.moistureByWeekDF,
            self.moistureByMonthDF,
            self.soilDF,
            self.ergotDF,
        )

        # onl fall months

    def getSets(self):
        #dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        return self.listOfSets
