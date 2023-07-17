import sqlalchemy

class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str) -> str: ...
    def readTableExists(
        self, results: sqlalchemy.engine.CursorResult
    ) -> bool: ...
