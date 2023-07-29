# ----------------------------------------------------
# GenericQueryBuilder.py
#
# Purpose: handles (builds/processes) general requests to a database
# ----------------------------------------------------
class GenericQueryBuilder:
    def tableExistsReq(self, tablename: str) -> str: ...
    def readTableExists(self, results) -> bool: ...
