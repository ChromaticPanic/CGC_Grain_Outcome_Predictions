import psycopg2, os
from dotenv import load_dotenv
from CSVBorderReader import CSVBorderReader

load_dotenv()
seedData = ''
borderReader = CSVBorderReader()
borderReader.read('provBoundaries.csv')
output = borderReader.getGISBorders()

for data in output:
    seedData += "INSERT INTO province (name, boundaries) VALUES(" + data[0] + ", " + data[1] + ");"

conn = psycopg2.connect(host=os.getenv('localhost'), port=os.getenv('5432'), database=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=os.getenv('POSTGRES_PW'))
curr = conn.cursor()

curr.execute(
    """
    CREATE TABLE province (
        ID SERIAL,
        name VARCHAR(2) NOT NULL,
        boundaries geography(MULTIPOLYGON) NOT NULL
    );
    """ + seedData
)

conn.commit()
conn.close()
curr.close()