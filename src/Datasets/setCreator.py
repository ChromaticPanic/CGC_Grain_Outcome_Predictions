# -------------------------------------------
# setCreator.py
#
# After loading the dataset, this class creates different datasets to be used in the modeling process
#
# Splits present:
# -------------------------------------------
# - Train (used to train the models)
# - Test (used to test the models)
# - Dev (used during hyperparameter testing, prevents overfitting the hyperparameters to the data)
#
# Datasets present:
# -------------------------------------------
# - Dataset1: Exploratory set (seasons, worst years, first 15 years, all data, different data preprocessing)
#
# - Dataset2: Best from dataset1 plus all data aggregated combinations (day, week, month)
#
# - Dataset3: Results from Feature Reduction on dataset2 (using RFECV and random forests)
#
# - Dataset4: Best results from dataset3, where the train and test sets are based on different years
#   - First 15 years aggregated by week [reduced]|[median]|[minMax]|[straified on has_ergot]
#
# - Dataset5: Second best results from dataset3, where the train and test sets are based on different years
#   - Moisture data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]
#
# Remarks:
# -------------------------------------------
#   - Data is searchable by its description, this means that if you want to learn more about the data from a particular model,
#     get its descript and search for it using control f
#
#   - Dataset1, Dataset2, Dataset3, Dataset4 and Dataset5 are not that great, they have iterropolation, unbalanced data and were tested using same year Ergot data
#   - The creation of these datasets depend heavily upon Sets, this means that while they dont have to be used these are their varying column requirements:
#       - year
#       - district
#       - The last column must adhere to the formats set by the [aggregatorHelper](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/Shared/aggregatorHelper.py)
#         i.e MO-DA:ATTRIBUTE, W:ATTRIBUTE, M:ATTRIBUTE
#   - Due the sheer size of this class, it is a singleton. This means only one instance can be created thus making it quicker to load afterwards
# -------------------------------------------
from dotenv import load_dotenv
import sqlalchemy as sq
import pandas as pd
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

from Sets.first15Yrs import First15Yrs  # type: ignore
from Sets.badErgot import BadErgot  # type: ignore
from Sets.complete import Complete  # type: ignore
from Sets.winter import Winter  # type: ignore
from Sets.spring import Spring  # type: ignore
from Sets.summer import Summer  # type: ignore
from Sets.fall import Fall  # type: ignore

from setModifier import SetModifier  # type: ignore

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

sys.path.append("../")
from Shared.GenericQueryBuilder import GenericQueryBuilder
from Shared.DataService import DataService
from Ergot.ergotAggregator import ErgotAggregator
from Soil.soilAggregator import SoilAggregator
from WeatherStation.hlyAggregator import HlyAggregator
from SatelliteSoilMoisture.moistureAggregator import MoistureAggregator


# Where we expect the find the loaded data (stored in CSVs since there are too many columns)
LOCAL_FILE_DATASETS_LOC = "./data"

# The CSV holding the hourly weather station data by day
HLY_CSV_BY_DAY = "agg_hly_by_day.csv"

# The CSV holding the hourly weather station data by week
HLY_CSV_BY_WEEK = "agg_hly_by_week.csv"

# The CSV holding the hourly weather station data by month
HLY_CSV_BY_MONTH = "agg_hly_by_month.csv"

# The CSV holding the soil moisture data by day
MOISTURE_CSV_BY_DAY = "agg_moisture_by_day.csv"

# The CSV holding the soil moisture data by week
MOISTURE_CSV_BY_WEEK = "agg_moisture_by_week.csv"

# The CSV holding the soil moisture data by month
MOISTURE_CSV_BY_MONTH = "agg_moisture_by_month.csv"

# The table that holds the aggregated soil data
AGG_SOIL_TABLE = "agg_soil_data"

# The table that holds the aggregated ergot data
AGG_ERGOT_TABLE = "agg_ergot_sample_v2"

# The queries used to get the soil and ergot data from the database
SOIL_QUERY = sq.text(f"SELECT * FROM {AGG_SOIL_TABLE};")
ERGOT_QUERY = sq.text(f"SELECT * FROM {AGG_ERGOT_TABLE};")


# Load the database connection environment variables located in the docker folder
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

load_dotenv("../docker/.env")
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


class SetCreator:
    def __init__(self):
        if (
            PG_DB is None
            or PG_ADDR is None
            or PG_PORT is None
            or PG_USER is None
            or PG_PW is None
        ):
            raise ValueError("Environment variables not set")

        db = DataService("postgres", "localhost", 5432, "postgres", "postgres")
        queryBuilder = GenericQueryBuilder()
        conn = db.connect()

        # checks if the data that is needed has been aggregated, if not, aggregate it
        self.__verifySoilIsAggregated(db, queryBuilder)
        self.__verifyErgotIsAggregated(db, queryBuilder)
        self.__verifyHlyIsAggregated(LOCAL_FILE_DATASETS_LOC)
        self.__verifyMoistureIsAggregated(LOCAL_FILE_DATASETS_LOC)

        # pull all data
        hlyByDayDF = pd.read_csv(f"{LOCAL_FILE_DATASETS_LOC}/{HLY_CSV_BY_DAY}")
        hlyByWeekDF = pd.read_csv(f"{LOCAL_FILE_DATASETS_LOC}/{HLY_CSV_BY_WEEK}")
        hlyByMonthDF = pd.read_csv(f"{LOCAL_FILE_DATASETS_LOC}/{HLY_CSV_BY_MONTH}")

        moistureByDayDF = pd.read_csv(
            f"{LOCAL_FILE_DATASETS_LOC}/{MOISTURE_CSV_BY_DAY}"
        )
        moistureByWeekDF = pd.read_csv(
            f"{LOCAL_FILE_DATASETS_LOC}/{MOISTURE_CSV_BY_WEEK}"
        )
        moistureByMonthDF = pd.read_csv(
            f"{LOCAL_FILE_DATASETS_LOC}/{MOISTURE_CSV_BY_MONTH}"
        )

        soilDF = pd.read_sql(SOIL_QUERY, conn)
        ergotDF = pd.read_sql(ERGOT_QUERY, conn)

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

    # Ensures this class is a singleton (only one instance can be created)
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SetCreator, cls).__new__(cls)
        return cls.instance

    def __verifySoilIsAggregated(
        self, db: DataService, queryBuilder: GenericQueryBuilder
    ):
        """
        Purpose:
        Checks if the soil data has been aggregated, if not, proceeds to aggregate it

        Table:
        - [agg_soil_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_soil_data)

        Pseudocode:
        - Generate query used to check if the table exists
        - Check if the table exists
        - If not start the aggregation process
        """
        query = sq.text(queryBuilder.tableExistsReq(AGG_SOIL_TABLE))
        tableExists = queryBuilder.readTableExists(db.execute(query))

        if not tableExists:
            SoilAggregator()

    def __verifyErgotIsAggregated(
        self, db: DataService, queryBuilder: GenericQueryBuilder
    ):
        """
        Purpose:
        Checks if the ergot data has been aggregated, if not, proceeds to aggregate it

        Table:
        - [agg_ergot_data](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions#agg_ergot_sample)

        Pseudocode:
        - Generate query used to check if the table exists
        - Check if the table exists
        - If not start the aggregation process
        """
        query = sq.text(queryBuilder.tableExistsReq(AGG_ERGOT_TABLE))
        tableExists = queryBuilder.readTableExists(db.execute(query))

        if not tableExists:
            ErgotAggregator()

    def __verifyHlyIsAggregated(self, path: str):
        """
        Purpose:
        Checks if the hourly weather station data has been aggregated, if not, proceeds to aggregate it

        Pseudocode:
        - Ensures the current directory is pointed to the same folder this file is located within
        - Check which csv files exist (by day, week and month)
        - If any are missing, start the aggregation process
        - For whichever ones are missing, continue the aggregation process (by day, week and month)

        Remarks: since there are too many columns, the data is instead stored in a CSV file
        """
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
                hlyAggregator.aggregateByDay(path, True)
            if not hasHlyByWeek:
                hlyAggregator.aggregateByWeek(path, True)
            if not hasHlyByMonth:
                hlyAggregator.aggregateByMonth(path, True)

    def __verifyMoistureIsAggregated(self, path):
        """
        Purpose:
        Checks if the soil moisture data has been aggregated, if not, proceeds to aggregate it

        Pseudocode:
        - Ensures the current directory is pointed to the same folder this file is located within
        - Check which csv files exist (by day, week and month)
        - If any are missing, start the aggregation process
        - For whichever ones are missing, continue the aggregation process (by day, week and month)

        Remarks: since there are too many columns, the data is instead stored in a CSV file
        """
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
                moistureAggregator.aggregateByDay(path, True)
            if not hasMoistureByWeek:
                moistureAggregator.aggregateByWeek(path, True)
            if not hasMoistureByMonth:
                moistureAggregator.aggregateByMonth(path, True)

    def getSetList1(self):
        """
        Purpose:
        Creates exploratory datasets (seasons, worst years, first 15 years, all data, different data preprocessing)
        These sets all try a variety of different data preprocessing techniques found in the [setModifier]()

        Pseudocode:
        The general way all these sets are created are as follows:
        1. [Load the data]()
        2. [Impute the data]()
        3. [Scale the data into train, test and dev]()
        4. Create a dictionary to hold the current set
        5. Give it a description (this also makes it easy to locate within this method)
        6. Assign the test, train and dev splits
        7. Append the data to the list of sets
        """
        setList = []  # Holds all the various datasets
        trainTestSet = {}  # Holds the current train test sets
        trainDevSet = {}  # Holds the current train dev sets ()

        # First 15 years aggregated by day [median]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByDay=True, moistureByDay=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
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

    def getSetList2(self):
        """
        Purpose:
        Creates exploratory datasets (best from dataset1 plus all data aggregated combinations (day, week, month))

        Pseudocode:
        The general way all these sets are created are as follows:
        1. [Load the data]()
        2. [Impute the data]()
        3. [Scale the data into train, test and dev]()
        4. Create a dictionary to hold the current set
        5. Give it a description (this also makes it easy to locate within this method)
        6. Assign the test, train and dev splits
        7. Append the data to the list of sets
        """
        setList = []  # Holds all the various datasets
        trainTestSet = {}  # Holds the current train test sets
        trainDevSet = {}  # Holds the current train dev sets ()

        # First 15 years aggregated by week [median]|[minMax]|[straified on has_ergot]
        currDF = self.first15Yrs.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        print(currDF.columns.tolist())
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [median]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data aggregated by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(
            hlyByMonth=True, moistureByMonth=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "Data aggregated by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data aggregated by week [mean]|[minMax]|[straified on has_ergot]
        currDF = self.complete.getCombinedDF(
            hlyByWeek=True, moistureByWeek=True, soil=True
        )
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "Data aggregated by week [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        return setList

    def getSetList3(self):
        """
        Purpose:
        Creates exploratory datasets (Results from Feature Reduction on dataset2 (using RFECV and random forests))

        Pseudocode:
        The general way all these sets are created are as follows:
        1. [Load the data]()
        2. [Impute the data]()
        3. [Scale the data into train, test and dev]()
        4. Create a dictionary to hold the current set
        5. Give it a description (this also makes it easy to locate within this method)
        6. Assign the test, train and dev splits
        7. Append the data to the list of sets
        """
        setList = []  # Holds all the various datasets
        trainTestSet = {}  # Holds the current train test sets
        trainDevSet = {}  # Holds the current train dev sets ()

        # First 15 years aggregated by week [reduced]|[median]|[minMax]|[straified on has_ergot]
        reducedSet = [
            "8:mean_temp",
            "10:min_temp",
            "10:max_temp",
            "28:max_temp",
            "28:max_humidex",
            "28:mean_humidex",
            "38:max_temp",
            "38:mean_temp",
            "38:max_humidex",
            "38:mean_humidex",
            "41:min_temp",
            "41:max_temp",
            "41:mean_temp",
            "41:max_dew_point_temp",
            "41:mean_dew_point_temp",
            "43:min_dew_point_temp",
            "43:mean_dew_point_temp",
            "50:min_temp",
            "51:max_temp",
            "51:max_dew_point_temp",
            "33:soil_moisture_max",
            "38:soil_moisture_max",
        ]
        reducedSet.extend(SetModifier.ERGOT_FEATURES)

        currDF = self.first15Yrs.getCombinedDF(hlyByWeek=True, moistureByWeek=True)
        currDF = currDF[reducedSet]
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [reduced]|[median]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data aggregated by month [reduced]|[mean]|[minMax]|[straified on has_ergot]
        reducedSet = [
            "2:min_temp",
            "2:max_temp",
            "2:max_dew_point_temp",
            "3:max_precip",
            "3:mean_precip",
            "4:max_temp",
            "4:mean_temp",
            "5:mean_temp",
            "7:mean_precip",
            "7:min_rel_humid",
            "7:mean_rel_humid",
            "9:max_temp",
            "9:mean_temp",
            "9:max_humidex",
            "9:mean_humidex",
            "12:mean_dew_point_temp",
            "12:max_precip",
            "12:mean_precip",
            "6:soil_moisture_max",
            "7:soil_moisture_min",
            "8:soil_moisture_min",
            "8:soil_moisture_max",
            "8:soil_moisture_mean",
            "9:soil_moisture_max",
        ]
        reducedSet.extend(SetModifier.ERGOT_FEATURES)

        currDF = self.complete.getCombinedDF(hlyByMonth=True, moistureByMonth=True)

        currDF = currDF[reducedSet]
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "Data aggregated by month [reduced]|[mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        # Data aggregated by week [reduced]|[mean]|[minMax]|[straified on has_ergot]
        reducedSet = [
            "2:mean_temp",
            "2:max_dew_point_temp",
            "2:mean_dew_point_temp",
            "6:max_temp",
            "6:max_dew_point_temp",
            "8:mean_temp",
            "28:mean_precip",
            "31:mean_temp",
            "36:max_temp",
            "36:mean_humidex",
            "38:max_temp",
            "38:max_humidex",
            "41:max_temp",
            "41:mean_temp",
            "43:max_temp",
            "43:max_dew_point_temp",
            "49:max_temp",
            "49:max_dew_point_temp",
            "50:max_precip",
            "50:mean_precip",
            "51:max_precip",
            "51:mean_precip",
            "33:soil_moisture_max",
            "34:soil_moisture_max",
            "34:soil_moisture_mean",
        ]
        reducedSet.extend(SetModifier.ERGOT_FEATURES)

        currDF = self.complete.getCombinedDF(hlyByWeek=True, moistureByWeek=True)

        currDF = currDF[reducedSet]
        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)
        trainTestSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])
        currDF = trainTestSet["train"]
        trainDevSet = self.modder.stratifiedSplit(currDF, currDF["has_ergot"])

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "Data aggregated by week [reduced]|[mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = trainTestSet["test"]
        dataDict["train"] = trainDevSet["train"]
        dataDict["dev"] = trainDevSet["test"]
        setList.append(dataDict)

        return setList

    def getSetList4(self):
        """
        Purpose:
        Creates exploratory datasets (best results from dataset3, where the train and test sets are based on different years)

        Pseudocode:
        The general way all these sets are created are as follows:
        1. [Load the data]()
        2. [Impute the data]()
        3. [Scale the data into train, test and dev]()
        4. Create a dictionary to hold the current set
        5. Give it a description (this also makes it easy to locate within this method)
        6. Assign the test, train splits
        7. Append the data to the list of sets
        """
        setList = []  # Holds all the various datasets

        # First 15 years aggregated by week [reduced]|[median]|[minMax]|[straified on has_ergot]
        reducedSet = [
            "8:mean_temp",
            "10:min_temp",
            "10:max_temp",
            "28:max_temp",
            "28:max_humidex",
            "28:mean_humidex",
            "38:max_temp",
            "38:mean_temp",
            "38:max_humidex",
            "38:mean_humidex",
            "41:min_temp",
            "41:max_temp",
            "41:mean_temp",
            "41:max_dew_point_temp",
            "41:mean_dew_point_temp",
            "43:min_dew_point_temp",
            "43:mean_dew_point_temp",
            "50:min_temp",
            "51:max_temp",
            "51:max_dew_point_temp",
            "33:soil_moisture_max",
            "38:soil_moisture_max",
        ]
        reducedSet.extend(SetModifier.ERGOT_FEATURES)

        currDF = self.first15Yrs.getCombinedDF(hlyByWeek=True, moistureByWeek=True)

        testDF = self.complete.getCombinedDF(hlyByWeek=True, moistureByWeek=True)

        testDF = testDF[~testDF.isin(currDF)]

        currDF = currDF[reducedSet]
        currDF = self.modder.InputeData(currDF, "median")
        currDF = self.modder.useMinMaxScaler(currDF)

        testDF = testDF[reducedSet]
        testDF = self.modder.InputeData(testDF, "median")
        testDF = self.modder.useMinMaxScaler(testDF)
        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "First 15 years aggregated by week [reduced]|[median]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = testDF
        dataDict["train"] = currDF
        setList.append(dataDict)

        return setList

    def getSetList5(self):
        """
        Purpose:
        Creates exploratory datasets (second best results from dataset3, where the train and test sets are based on different years)

        Pseudocode:
        The general way all these sets are created are as follows:
        1. [Load the data]()
        2. [Impute the data]()
        3. [Scale the data into train, test and dev]()
        4. Create a dictionary to hold the current set
        5. Give it a description (this also makes it easy to locate within this method)
        6. Assign the test, train splits
        7. Append the data to the list of sets
        """
        setList = []  # Holds all the various datasets

        # Moisture data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]
        currDF = self.badErgot.getCombinedDF(moistureByMonth=True)

        testDF = self.complete.getCombinedDF(moistureByMonth=True)
        testDF = testDF[~testDF.isin(currDF)]

        currDF = self.modder.InputeData(currDF, "mean")
        currDF = self.modder.useMinMaxScaler(currDF)

        testDF = self.modder.InputeData(testDF, "median")
        testDF = self.modder.useMinMaxScaler(testDF)

        dataDict = {"desc": "", "test": None, "train": None, "dev": None}
        dataDict[
            "desc"
        ] = "Moisture data from years with bad ergot aggregated by month [mean]|[minMax]|[straified on has_ergot]"
        dataDict["test"] = testDF
        dataDict["train"] = currDF
        setList.append(dataDict)

        return setList
