# ----------------------------------------------------
# DataService.pyi
#
# Handles communications with PostgreSQL databases
#
# Typical usage example:
#   db = DataService()
#   conn = db.connect()
#   db.execute(query: str)
#   db.cleanup()
# ----------------------------------------------------
import sqlalchemy as sq

class DataService:
    dbURL: str
    engine: sq.engine.base.Engine
    conn: sq.engine.base.Connection
    def __init__(
        self,
        db: str = ...,
        addr: str = ...,
        port: int = ...,
        user: str = ...,
        pw: str = ...,
    ) -> None: ...
    def connect(self) -> sq.engine.base.Connection: ...
    # ----------------------------------------------------
    # Purpose:
    # Connect to PostgreSQL database
    # ----------------------------------------------------

    def disconnect(self): ...
    # ----------------------------------------------------
    # Purpose:
    # Disconnect from PostgreSQL database
    # ----------------------------------------------------

    def cleanup(self): ...
    # ----------------------------------------------------
    # Purpose:
    # Cleanup operation: close open connections
    # ----------------------------------------------------

    def execute(self, query) -> object: ...
    # ----------------------------------------------------
    # Purpose:
    # Execute a query on the database
    # ----------------------------------------------------
