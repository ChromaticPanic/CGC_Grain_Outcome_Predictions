from sets.first15Yrs import First15Yrs
from sets.badErgot import BadErgot
from sets.complete import Complete
from sets.winter import Winter
from sets.spring import Spring
from sets.summer import Summer
from sets.fall import Fall


class SetCreator:
    def __new__(cls): 
        if not hasattr(cls, 'instance'):
            cls.instance = super(SetCreator, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.listOfSets = []
        
        self.addFirst15Yrs()
        self.addBadErgot()
        self.addComplete()
        self.addWinter()
        self.addSpring()
        self.addSummer()
        self.addFall()


    def addFirst15Yrs(self):
        first15Yrs = First15Yrs()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # first 15 years by week, soil moisture, soil
        # first 15 years by day, soil moisture, soil, weather

    def addBadErgot(self):
        badErgot = BadErgot()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # year ergot was worst weather by month
        # year ergot was soil
        # year ergot was worst soil moisture

    def addComplete(self):
        complete = Complete()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # all for weather by month
        # add for weather by week
        # all for weather by day

        # all for soil moisture and moisture by month
        # all for soil moisture and moisture by week
        # all for soil moisture and moisture by day

        # all for weather and soil moisture by month
        # all for weather and soil moisture and soil by month
        # add for weather and soil moisture by week
        # add for weather and soil moisture and soil by week
        # all for weather and soil moisture by day
        # all for weather and soil moisture and soil by day

    def addWinter(self):
        winter = Winter()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # only dataset on winter months

    def addSpring(self):
        spring = Spring()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # onl spring months

    def addSummer(self):
        summer = Summer()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # only dataset on summer months

    def addFall(self):
        fall = Fall()
        dataDict = {"desc": '', "test": None, "train": None, "dev": None}

        # onl fall months

    def getSets(self):
        return self.listOfSets