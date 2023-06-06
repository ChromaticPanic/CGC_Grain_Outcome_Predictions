# eventually the goal is to create data folders. You then drop the files you want to read the data from
# after reading the data these files then get moved else where
from QueryHandler import QueryHandler
from dotenv import load_dotenv
import sys, math, pandas

sys.path.append('../')
from DataService import DataService


FILENAME = 'ergot1995-2022' # the name of the file you want to read
TABLENAME = 'ergot_sample'  # the name of the table where the data should be stored
EXPECTED_COLS = ['Year', 'ProvinceAbbr', 'CropDistrictCode', 'Incidence', 'Severity']   # the expected csv column names
RENAMED_COLS = ['year', 'province', 'crop_district', 'incidence', 'severity']           # the desired database column names

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')
PG_PORT = os.getenv('POSTGRES_PORT')

def main():
    ergotSamples = pandas.read_csv(f'./data/{FILENAME}.csv')    # Holds the ergot data to import
    db = DataService(PG_DB, PG_ADDR, PG>PORT, PG_USER, PG_PW)   # Handles connections to the database
    conn = db.connect()                                         # Connect to the database
    
    queryHandler = QueryHandler()   # Handles (builds/processes) requests to the database
    ommitedData = []                # Holds data that failed to meet constraint (and was thus ommited)

    checkAttributes(ergotSamples, EXPECTED_COLS)
    checkTable(db, queryHandler)

    # For each sample, verify the data
    for index, sample in ergotSamples.iterrows(): 
        validYear = not None and sample[EXPECTED_COLS[0]] > 0
        validProv = not None and len(sample[EXPECTED_COLS[1]]) == 2
        validCode = not None and sample[EXPECTED_COLS[2]] > 0
        validIncidence = not None and (sample[EXPECTED_COLS[3]] == 0 or sample[EXPECTED_COLS[3]] == 1)
        validSeverity = math.isnan(sample[EXPECTED_COLS[4]]) or (sample[EXPECTED_COLS[4]] >= 0 and sample[EXPECTED_COLS[4]] <= 100)

        # If data fails to meet requirements, save for later 
        if not validYear or not validProv or not validCode or not validIncidence or not validSeverity:
            ommitedData.append({'index': index, 'sample': sample})

    # Remove the data that failed to meet requirements 
    for data in ommitedData:
        ergotSamples.drop(data['index'], inplace=True)

    # Drops extra attributes and renames columns
    dropExtraAttributes(ergotSamples, EXPECTED_COLS)
    ergotSamples.rename(columns={ergotSamples.columns[0]: RENAMED_COLS[0]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[1]: RENAMED_COLS[1]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[2]: RENAMED_COLS[2]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[3]: RENAMED_COLS[3]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[4]: RENAMED_COLS[4]}, inplace=True)

    # Sets the according data type for each attribute
    ergotSamples[['province']] = ergotSamples[['province']].astype(str)
    ergotSamples[['severity']] = ergotSamples[['severity']].astype(float)
    ergotSamples[['incidence']] = ergotSamples[['incidence']].astype(bool)
    ergotSamples[['year', 'crop_district']] = ergotSamples[['year', 'crop_district']].astype(int)  
 
    # Stores the resulting data
    rowsAffected = ergotSamples.to_sql(TABLENAME, conn, schema='public', if_exists="append", index=False)

    print(f'[SUCCESS] added {rowsAffected}/{len(ergotSamples)} ergot data samples from {FILENAME}.csv')
    print(f'{len(ergotSamples) - rowsAffected} samples were ommited due to data constraints, they are as follows')
    for sample in ommitedData:
        print(f'\t{sample["index"]}: {sample["sample"]}')

    db.cleanup()


def checkAttributes(data: pandas.Dataframe, expectedCols: []):
    for col in expectedCols:        # For each of the expected columns
        if not col in data.keys():  # check if its in the dataframe
            print(f'[ERROR] ergot sample file is missing the expected attribute: {col}')
            sys.exit()

def checkTable(db: DataService, queryHandler: QueryHandler):
    # Checks if the table needed to run the pipeline has been created, if not creates it
    query = sq.text(queryHandler.tableExistsReq(TABLENAME))         # Create the command needed to check if the table exists
    tableExists = queryHandler.readTableExists(db.execute(query))

    if not tableExists:
        query = sq.text(queryHandler.createErgotSampleTableReq())   # Create the command needed to create the table
        db.execute(query)

def dropExtraAttributes(data: pandas.Dataframe, requiredCol: []):
    attributesToDrop = []                   # Stores the extra attributes we wish to drop

    for attr in data.keys():                # For each attribute in the dataframe
        if attr not in requiredCol:         # Check if its one of the attributes we want
            attributesToDrop.append(attr)

    for attr in attributesToDrop:           # Drop all unnecessary attributes
        data.drop(attr, axis=1, inplace=True)


if __name__ == "__main__":
    main()