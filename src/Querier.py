class Querier:
    def tableExistsReq(self, tablename):
        return f"""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = \'public\' AND tablename  = \'{tablename}\'
        );
        """

    def readTableExists(self, results):
        return results.first()[0]