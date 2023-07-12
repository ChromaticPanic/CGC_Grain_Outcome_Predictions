import sqlalchemy  # type: ignore

class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str) -> str: ...
    def readTableExists(
        self, results: sqlalchemy.engine.cursor.CursorResult
    ) -> bool: ...
