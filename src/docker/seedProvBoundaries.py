from dotenv import load_dotenv
import psycopg2, os

load_dotenv()

conn = psycopg2.connect(host=os.getenv('localhost'), port=os.getenv('5432'), database=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=os.getenv('POSTGRES_PW'))

curr = conn.cursor()

curr.execute(
    """
    CREATE TABLE province (
        ID SERIAL,
        name VARCHAR(2) NOT NULL,
        boundaries geography(MULTIPOLYGON) NOT NULL
    );
    """
)

#now read in CSV

conn.commit()
conn.close()
curr.close()