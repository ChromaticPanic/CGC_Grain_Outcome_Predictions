"""DataService handles communication with PostgreSQL database

-

Typical usage example:

  
"""
import atexit
import sqlalchemy as sq

class DataService:
    def __init__(self, db: str = "postgres", user: str = "postgres", pw: str = "password") -> None:
        self.dbURL = f"postgresql://{user}:{pw}@localhost:5432/{db}"
        self.engine = sq.create_engine(self.dbURL)
        self.conn = None
        atexit.register(self.cleanup)

    def connect(self) -> object:
        """Connect to PostgreSQL database"""
        self.conn = self.engine.connect()
        return self.conn

    def disconnect(self) -> None:
        """Disconnect from PostgreSQL database"""
        self.conn.close()
        self.engine.dispose()

    def cleanup(self) -> None:
        """Cleanup operations"""
        if self.conn is not None:
            self.disconnect()

    def execute(self, query) -> object:
        """Execute a query on the database"""
        return self.conn.execute(query)
