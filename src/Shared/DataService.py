"""DataService handles communication with PostgreSQL database

-

Typical usage example:

  
"""
import atexit
import sqlalchemy as sq
from _typeshed import Incomplete

class DataService:
    dbURL: Incomplete
    engine: Incomplete
    conn: Incomplete
    def __init__(self, db: str = ..., addr: str = ..., port: int = ..., user: str = ..., pw: str = ...) -> None: ...
    def connect(self) -> sq.Connection: ...
    def disconnect(self) -> None: ...
    def cleanup(self) -> None: ...
    def execute(self, query) -> object: ...

    def __init__(
        self,
        db: str = "postgres",
        addr: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        pw: str = "password",
    ) -> None:
        self.dbURL: str = f"postgresql://{user}:{pw}@{addr}:{port}/{db}"
        self.engine: sq.Engine = sq.create_engine(self.dbURL)
        self.conn: sq.Connection = self.connect()
        atexit.register(self.cleanup)

    def connect(self) -> sq.Connection:
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
