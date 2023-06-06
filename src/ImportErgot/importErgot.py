# this file will need manual confirmation on this data/all data sources present for download in data folder
from QueryHandler import QueryHandler
from dotenv import load_dotenv
import sys, math, pandas

sys.path.append('../')
from DataService import DataService


FILENAME = 'ergot1995-2022'
TABLENAME = 'ergot_sample'
EXPECTED_COLS = ['Year', 'ProvinceAbbr', 'CropDistrictCode', 'Incidence', 'Severity']
RENAMED_COLS = ['year', 'province', 'crop_district', 'incidence', 'severity']

load_dotenv()
PG_USER = os.getenv('POSTGRES_USER')
PG_PW = os.getenv('POSTGRES_PW')
PG_DB = os.getenv('POSTGRES_DB')
PG_ADDR = os.getenv('POSTGRES_ADDR')

def main():
    ergotSamples = pandas.read_csv(f'./data/{FILENAME}.csv')
    db = DataService(PG_DB, PG_USER, PG_PW) # Handles connections to the database
    conn = db.connect()                     # connect to the database
    
    queryHandler = QueryHandler()
    ommitedData = []

    checkAttributes(ergotSamples, EXPECTED_COLS)
    checkTable(db, queryHandler)

    for index, sample in ergotSamples.iterrows(): 
        validYear = not None and sample[EXPECTED_COLS[0]] > 0
        validProv = not None and len(sample[EXPECTED_COLS[1]]) == 2
        validCode = not None and sample[EXPECTED_COLS[2]] > 0
        validIncidence = not None and (sample[EXPECTED_COLS[3]] == 0 or sample[EXPECTED_COLS[3]] == 1)
        validSeverity = math.isnan(sample[EXPECTED_COLS[4]]) or (sample[EXPECTED_COLS[4]] >= 0 and sample[EXPECTED_COLS[4]] <= 100)

        if not validYear or not validProv or not validCode or not validIncidence or not validSeverity:
            ommitedData.append({'index': index, 'sample': sample})

    for data in ommitedData:
        ergotSamples.drop(data['index'], inplace=True)

    dropExtraAttributes(ergotSamples, EXPECTED_COLS)
    ergotSamples.rename(columns={ergotSamples.columns[0]: RENAMED_COLS[0]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[1]: RENAMED_COLS[1]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[2]: RENAMED_COLS[2]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[3]: RENAMED_COLS[3]}, inplace=True)
    ergotSamples.rename(columns={ergotSamples.columns[4]: RENAMED_COLS[4]}, inplace=True)

    ergotSamples[['province']] = ergotSamples[['province']].astype(str)
    ergotSamples[['severity']] = ergotSamples[['severity']].astype(float)
    ergotSamples[['incidence']] = ergotSamples[['incidence']].astype(bool)
    ergotSamples[['year', 'crop_district']] = ergotSamples[['year', 'crop_district']].astype(int)  
 
    rowsAffected = ergotSamples.to_sql(TABLENAME, conn, schema='public', if_exists="append", index=False)

    print(f'[SUCCESS] added {rowsAffected}/{len(ergotSamples)} ergot data samples from {FILENAME}.csv')
    print(f'{len(ergotSamples) - rowsAffected} samples were ommited due to data constraints, they are as follows')
    for sample in ommitedData:
        print(f'\t{sample["index"]}: {sample["sample"]}')

    db.cleanup()


def checkAttributes(data, expectedCols):
    for col in expectedCols:
        if not col in data.keys():
            print(f'[ERROR] ergot sample file is missing the expected attribute: {col}')
            sys.exit()

def checkTable(db, queryHandler):
    query = sq.text(queryHandler.tableExistsReq(TABLENAME))
    tableExists = queryHandler.readTableExists(db.execute(query))
    if not tableExists:
        query = sq.text(queryHandler.createErgotSampleTableReq())
        db.execute(query)

def dropExtraAttributes(data, requiredCol):
    attributesToDrop = []

    for attr in data.keys():
        if attr not in requiredCol:
            attributesToDrop.append(attr)

    for attr in attributesToDrop:
        data.drop(attr, axis=1, inplace=True)

if __name__ == "__main__":
    main()