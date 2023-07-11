from dotenv import load_dotenv
import sqlalchemy as sq  # type: ignore
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

from setModifier import SetModifier

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService
from Ergot.ergotAggregator import ErgotAggregator
from importSoil.soilAggregator import SoilAggregator
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
        self.__verifySoilIsAggregated(db, queryBuilder)
        self.__verifyErgotIsAggregated(db, queryBuilder)
        self.__verifyHlyIsAggregated(LOCAL_FILE_DATASETS_LOC)
        self.__verifyMoistureIsAggregated(LOCAL_FILE_DATASETS_LOC)

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

        self.modder = SetModifier()

        self.first15Yrs = First15Yrs(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

        self.badErgot = BadErgot(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

        self.complete = Complete(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

        self.winter = Winter(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

        self.spring = Spring(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

        self.summer = Summer(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

        self.fall = Fall(
            hlyByDayDF,
            hlyByWeekDF,
            hlyByMonthDF,
            moistureByDayDF,
            moistureByWeekDF,
            moistureByMonthDF,
            soilDF,
            ergotDF,
        )

    def __verifySoilIsAggregated(self, db, queryBuilder):
        query = sq.text(queryBuilder.tableExistsReq(AGG_SOIL_TABLE))
        tableExists = queryBuilder.readTableExists(db.execute(query))

        if not tableExists:
            SoilAggregator()

    def __verifyErgotIsAggregated(self, db, queryBuilder):
        query = sq.text(queryBuilder.tableExistsReq(AGG_ERGOT_TABLE))
        tableExists = queryBuilder.readTableExists(db.execute(query))

        if not tableExists:
            ErgotAggregator()

    def __verifyHlyIsAggregated(self, path):
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

    def __verifyMoistureIsAggregated(self, path):
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


    def getSetList1(self):
        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        setList = []
        trainTestSet = {}
        trainDevSet = {}

        # First 15 years aggregated by day [median]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByDay=True, moistureByDay=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by day [median]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by day [median]|[StandardScalar]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByDay=True, moistureByDay=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by day [median]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by day [median]|[bellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByDay=True, moistureByDay=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by day [median]|[bellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by day [median]|[bellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByDay=True, moistureByDay=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by day [median]|[bellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by week [median]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [median]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by week [median]|[StandardScalar]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [median]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by week [median]|[bellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [median]|[bellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by week [median]|[bellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [median]|[bellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by month [median]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by month [median]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by month [median]|[StandardScalar]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by month [median]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by month [median]|[bellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by month [median]|[bellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # First 15 years aggregated by month [median]|[bellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "First 15 years aggregated by month [median]|[bellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by day [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Hourly data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by day [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Hourly data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by day [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Hourly data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by week [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by week [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Hourly data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by week [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Hourly data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by month [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by month [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Hourly data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data by month [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(hlyByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by day [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by day [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by day [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by day [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by day [mean]|[BellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by day [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by day [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by week [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by week [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by week [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by week [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by week [mean]|[BellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by week [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by week [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by month [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by month [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by month [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by month [mean]|[BellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data by month [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(moistureByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data by month [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Soil data [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(soil=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Soil data [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Soil data [mean]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(soil=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Soil data [mean]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Soil data [mean]|[BellCurve]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(soil=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Soil data [mean]|[BellCurve]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Soil data [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(soil=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.attemptBellCurve(currDF)
        currDF = self.modder.useStandardScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Soil data [mean]|[BellCurve]|[StandardScalar]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Winter data [mean]|[minMax]|[straified on has_ergot]
        currDF = self.winter.getCombinedDF(True, True, True, True, True, True, True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Winter data [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Spring data [mean]|[minMax]|[straified on has_ergot]
        currDF = self.spring.getCombinedDF(True, True, True, True, True, True, True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Spring data [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Summer data [mean]|[minMax]|[straified on has_ergot]
        currDF = self.summer.getCombinedDF(True, True, True, True, True, True, True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Summer data [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Fall data [mean]|[minMax]|[straified on has_ergot]
        currDF = self.fall.getCombinedDF(True, True, True, True, True, True, True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict["desc"] = "Fall data [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # All data aggregated by day [mean]|[minMax]|[straified on has_ergot]
        currDF = self.fall.getCombinedDF(hlyByDay=True, moistureByDay=True, soil=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "All data aggregated by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # All data aggregated by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.fall.getCombinedDF(hlyByWeek=True, moistureByWeek=True, soil=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "All data aggregated by week [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # All data aggregated by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.fall.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "All data aggregated by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data from years with bad ergot aggregated by day [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(hlyByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data from years with bad ergot aggregated by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data from years with bad ergot aggregated by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(hlyByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data from years with bad ergot aggregated by week [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Hourly data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(hlyByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Hourly data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture from years with bad ergot aggregated by day [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(moistureByDay=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data from years with bad ergot aggregated by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data from years with bad ergot aggregated by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(moistureByWeek=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data from years with bad ergot aggregated by week [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Moisture data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(moistureByMonth=True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Moisture data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data from years with bad ergot aggregated by day [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(
            hlyByDay=True, moistureByDay=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Data from years with bad ergot aggregated by day [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data from years with bad ergot aggregated by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "# Data from years with bad ergot aggregated by week [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data from years with bad ergot [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(True, True, True, True, True, True, True)
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        dataDict[
            "desc"
        ] = "Data from years with bad ergot [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        return setList
