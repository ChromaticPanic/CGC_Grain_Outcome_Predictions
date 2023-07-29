# ----------------------------------------------------
# GenericQueryBuilder.py
#
# Purpose: handles (builds/processes) general requests to a database
# ----------------------------------------------------
class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str) -> str:
        return f"""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = \'public\' AND tablename  = \'{tablename}\'
        );
        """

    def readTableExists(self, results) -> bool:
        if hasattr(results, "first"):
            return results.first() is not None
        return False
