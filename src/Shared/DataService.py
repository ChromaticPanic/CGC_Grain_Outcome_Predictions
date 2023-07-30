# ----------------------------------------------------
# DataService.py
#
# Handles communications with PostgreSQL databases
#
# Typical usage example:
#   db = DataService()
#   conn = db.connect()
#   db.execute(query: str)
#   db.cleanup()
# ----------------------------------------------------
import atexit
import sqlalchemy as sq


class DataService:
    dbURL: str
    engine: sq.engine.base.Engine
    conn: sq.engine.base.Connection

    def __init__(
        self,
        db: str = "postgres",
        addr: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        pw: str = "password",
    ):
        self.dbURL: str = f"postgresql://{user}:{pw}@{addr}:{port}/{db}"
        self.engine: sq.engine.base.Engine = sq.create_engine(self.dbURL)
        self.conn: sq.engine.base.Connection = self.connect()
        atexit.register(self.cleanup)  # Ensures that connections eventually closed

    def connect(self) -> sq.engine.base.Connection:
        """
        Purpose:
        Connect to PostgreSQL database
        """
        self.conn = self.engine.connect()
        return self.conn

    def disconnect(self):
        """
        Purpose:
        Disconnect from PostgreSQL database
        """
        self.conn.close()
        self.engine.dispose()

    def cleanup(self):
        """
        Purpose:
        Cleanup operation: close open connections
        """
        if self.conn is not None:
            self.disconnect()

    def execute(self, query) -> object:  # type: ignore
        """
        Purpose:
        Execute a query on the database
        """
        return self.conn.execute(query)
