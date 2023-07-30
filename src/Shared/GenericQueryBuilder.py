# ----------------------------------------------------
# GenericQueryBuilder.py
#
# Purpose: handles (builds/processes) general requests to a database
# ----------------------------------------------------
class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str, schema: str = "public") -> str:
        """
        Purpose:
        Generates a SQL query to see if a table exists in a database
        """
        return f"""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = \'{schema}\' AND tablename = \'{tablename}\'
        );
        """

    def readTableExists(self, results) -> bool:
        """
        Purpose:
        Checks if a table exists in a database

        Pseudocode:
        - Check results has an attribute called [first](https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.first)
        """
        if hasattr(results, "first"):
            return results.first() is not None
        return False
