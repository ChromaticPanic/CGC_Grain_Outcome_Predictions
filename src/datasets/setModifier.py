from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn.preprocessing import MinMaxScaler  # type: ignore
from sklearn.impute import SimpleImputer  # type: ignore
from scipy import stats  # type: ignore
import pandas as pd  # type: ignore
import numpy as np


class SetModifier:
    def InputeData(self, df, strat):
        if strat == "zero" or strat == "mean" or strat == "median" or strat == "mode":
            imputer = SimpleImputer(strategy=strat)
            df = imputer.fit_transform(df)

        return df

    def attemptBellCurve(self, df):
        colList = df.columns.tolist()

        for col in colList:
            results = stats.shapiro(df[col])

            # if this is true, we assume the data does not create a bell curve
            if results.pvalue <= 0.05:
                logData = np.log(df[col])
                sqrtData = np.sqrt(df[col])
                cbrtRoot = np.cbrt(df[col])

                logResults = stats.shapiro(logData)
                sqrtResults = stats.shapiro(sqrtData)
                cbrtResults = stats.shapiro(cbrtRoot)

                # Check if any of these transformations appear any better, if so replace the data with it
                if logResults.pvalue > 0.05:
                    df[col] = logData
                elif sqrtResults.pvalue > 0.05:
                    df[col] = sqrtData
                elif cbrtResults.pvalue > 0.05:
                    df[col] = cbrtRoot

        return df

    def useMinMaxScaler(self, df, forNeuralNetwork: bool = False):
        scaler = (
            MinMaxScaler(feature_range=(-1, 1))
            if forNeuralNetwork
            else MinMaxScaler(feature_range=(0, 1))
        )

        return scaler.fit_transform(df)

    def useStandardScaler(self, df):
        scaler = StandardScaler()

        return scaler.fit_transform(df)

    def randomSplit(
        self, df: pd.DataFrame, testSize: float = 0.2, randomSeed: int = 42
    ) -> dict:
        train_set, test_set = train_test_split(
            df, test_size=testSize, random_state=randomSeed
        )

        return {"trainSet": train_set, "test_set": test_set}

    def stratifiedSplit(
        self,
        df: pd.DataFrame,
        descrimRow,
        testSize: float = 0.2,
        randomSeed: int = 42,
    ) -> dict:
        train_set, test_set = train_test_split(
            df, stratify=descrimRow, test_size=testSize, random_state=randomSeed
        )

        return {"trainSet": train_set, "test_set": test_set}
