import sys

sys.path.append('../')
from Querier import Querier


class QueryHandler(Querier):
    def createCopernicusTableReq(self):
        print()

    def createRowExistsInDBReq(self, lon, lat, datetime):
        print()
        
    def readRowExistsInDB(self, results):
        print()

    def createInsertRowReq(self):
        print()

    def createUpdateRowReq(self):
        print()
        # create table if you need to
    # lat, long, area, attrs, time - year, month, day, hour

    # check if lat, long and time are in db