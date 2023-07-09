from sklearn.model_selection import train_test_split 
import pandas as pd

class DataSetGenerator():

    def randomSplit(self, data: pd.DataFrame, testSize: float=0.2, randomSeed: int=42) -> dict:
        train_set, test_set = train_test_split(data, test_size=testSize, random_state=randomSeed)

        return {"trainSet": train_set, "test_set": test_set}

    def stratifiedSplit(self, data: pd.DataFrame, descrimRow, testSize: float=0.2, randomSeed: int=42) -> dict:
        strat_train_set, strat_test_set = train_test_split(data, stratify=descrimRow, test_size=testSize, random_state=randomSeed) 

        return {"trainSet": strat_train_set, "test_set": strat_test_set}