# ----------------------------------------------------
# Querier.py
#
# Purpose: handles (builds/processes) requests to a database
# ----------------------------------------------------
import sqlalchemy


class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str) -> str:
        return f"""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = \'public\' AND tablename  = \'{tablename}\'
        );
        """

    def readTableExists(self, results: sqlalchemy.engine.CursorResult) -> bool:
        return results.first() is not None
