# ----------------------------------------------------
# Querier.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------
import sqlalchemy

class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str) -> str: ...
    def readTableExists(self, results: sqlalchemy.engine.cursor.CursorResult) -> bool: ...

    def tableExistsReq(self, tablename: str) -> str:
        return f"""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = \'public\' AND tablename  = \'{tablename}\'
        );
        """

    def readTableExists(self, results: sqlalchemy.engine.cursor.CursorResult) -> bool:
        row = results.first()
        if row is None:
            return False
        return row[0]
