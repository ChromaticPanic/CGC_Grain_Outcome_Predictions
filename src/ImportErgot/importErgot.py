# ----------------------------------------------------
# ImportErgot.py
#
# Purpose: to validate then store ergot data samples into a database
#
# Remarks:
# - Eventually the goal is to create data folders. You then drop the files you want to read the data from
#   after reading the data these files then get moved else where
# ----------------------------------------------------
from ImportErgot.ErgotQueryBuilder import ErgotQueryBuilder
from dotenv import load_dotenv
import os, sys, math, pandas, sqlalchemy

sys.path.append("../")
from DataService import DataService


FILENAME = "newErgot"  # the name of the file you want to read
TABLENAME = "ergot_sample"  # the name of the table where the data should be stored
EXPECTED_COLS = [
    "Year",
    "ProvinceAbbr",
    "CropDistrictCode",
    "Incidence",
    "Severity",
]  # the expected csv column names
RENAMED_COLS = [
    "year",
    "province",
    "crop_district",
    "incidence",
    "severity",
]  # the desired database column names

load_dotenv()
PG_DB = os.getenv("POSTGRES_DB")
PG_ADDR = os.getenv("POSTGRES_ADDR")
PG_PORT = int(os.getenv("POSTGRES_PORT"))
PG_USER = os.getenv("POSTGRES_USER")
PG_PW = os.getenv("POSTGRES_PW")


def main():
    ergotSamples = pandas.read_csv(
        f"./data/{FILENAME}.csv"
    )  # Holds the ergot data to import
    db = DataService(
        PG_DB, PG_ADDR, PG_PORT, PG_USER, PG_PW
    )  # Handles connections to the database
    conn = db.connect()  # Connect to the database

    queryHandler = ErgotQueryBuilder()  # Handles (builds/processes) requests to the database
    ommitedData = []  # Holds data that failed to meet constraint (and was thus ommited)

    checkAttributes(ergotSamples, EXPECTED_COLS)
    checkTable(db, queryHandler)

    # For each sample, verify the data
    for index, sample in ergotSamples.iterrows():
        validYear = not None and sample[EXPECTED_COLS[0]] > 0
        validProv = not None and len(sample[EXPECTED_COLS[1]]) == 2
        validCode = sample[EXPECTED_COLS[2]] > 0
        validIncidence = not None and (
            sample[EXPECTED_COLS[3]] == 0 or sample[EXPECTED_COLS[3]] == 1
        )
        validSeverity = (
            sample[EXPECTED_COLS[4]] >= 0 and sample[EXPECTED_COLS[4]] <= 100
        )

        # Both CropDistrictCode and Severity can be Null, but if thats the case they need to be manually adjusted
        if math.isnan(sample[EXPECTED_COLS[2]]):
            sample[EXPECTED_COLS[2]] = None
            validCode = True
        if math.isnan(sample[EXPECTED_COLS[4]]):
            sample[EXPECTED_COLS[4]] = None
            validSeverity = True

        # If data fails to meet requirements, save for later
        if (
            not validYear
            or not validProv
            or not validCode
            or not validIncidence
            or not validSeverity
        ):
            ommitedData.append({"index": index, "sample": sample})

    # Remove the data that failed to meet requirements
    for data in ommitedData:
        ergotSamples.drop(data["index"], inplace=True)

    # Drops extra attributes and renames columns
    dropExtraAttributes(ergotSamples, EXPECTED_COLS)
    ergotSamples.rename(
        columns={ergotSamples.columns[0]: RENAMED_COLS[0]}, inplace=True
    )
    ergotSamples.rename(
        columns={ergotSamples.columns[1]: RENAMED_COLS[1]}, inplace=True
    )
    ergotSamples.rename(
        columns={ergotSamples.columns[2]: RENAMED_COLS[2]}, inplace=True
    )
    ergotSamples.rename(
        columns={ergotSamples.columns[3]: RENAMED_COLS[3]}, inplace=True
    )
    ergotSamples.rename(
        columns={ergotSamples.columns[4]: RENAMED_COLS[4]}, inplace=True
    )

    # Sets the according data type for each attribute
    ergotSamples[["province"]] = ergotSamples[["province"]].astype(str)
    ergotSamples[["severity"]] = ergotSamples[["severity"]].astype(float)
    ergotSamples[["incidence"]] = ergotSamples[["incidence"]].astype(bool)
    ergotSamples[["year"]] = ergotSamples[["year"]].astype(int)

    # Stores the resulting data (not using return value due to its inaccuracy)
    ergotSamples.to_sql(
        TABLENAME, conn, schema="public", if_exists="append", index=False
    )

    print(
        f"[SUCCESS] added {len(ergotSamples) - len(ommitedData)}/{len(ergotSamples)} ergot data samples from {FILENAME}.csv"
    )
    if len(ommitedData) > 0:
        print(
            f"{len(ommitedData)} samples were ommited due to data constraints, they are as follows:"
        )

        for sample in ommitedData:
            print(f'\t{sample["index"]}: {sample["sample"]}')

    db.cleanup()


def checkAttributes(data: pandas.DataFrame, expectedCols: list):
    for col in expectedCols:  # For each of the expected columns
        if not col in data.keys():  # check if its in the dataframe
            print(f"[ERROR] ergot sample file is missing the expected attribute: {col}")
            sys.exit()


def checkTable(db: DataService, queryHandler: ErgotQueryBuilder):
    # Checks if the table needed to run the pipeline has been created, if not creates it
    query = sqlalchemy.text(
        queryHandler.tableExistsReq(TABLENAME)
    )  # Create the command needed to check if the table exists
    tableExists = queryHandler.readTableExists(db.execute(query))

    if not tableExists:
        query = sqlalchemy.text(
            queryHandler.createErgotSampleTableReq()
        )  # Create the command needed to create the table
        db.execute(query)


def dropExtraAttributes(data: pandas.DataFrame, requiredCol: list):
    attributesToDrop = []  # Stores the extra attributes we wish to drop

    for attr in data.keys():  # For each attribute in the dataframe
        if attr not in requiredCol:  # Check if its one of the attributes we want
            attributesToDrop.append(attr)

    for attr in attributesToDrop:  # Drop all unnecessary attributes
        data.drop(attr, axis=1, inplace=True)


if __name__ == "__main__":
    main()
