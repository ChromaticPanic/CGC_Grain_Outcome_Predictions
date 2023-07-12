from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn.preprocessing import MinMaxScaler  # type: ignore
from scipy import stats  # type: ignore
import pandas as pd
import numpy as np
import math


class SetModifier:
    ERGOT_PREDICTORS = [
        "percnt_true",
        "sum_severity",
        "ergot_present_in_q3",
        "ergot_present_in_q4",
        "sum_severity_in_q3",
        "sum_severity_in_q4",
    ]
    ERGOT_FEATURES = [
        "percnt_true",
        "has_ergot",
        "median_severity",
        "sum_severity",
        "present_in_neighbor",
        "sum_severity_in_neighbor",
        "present_prev1",
        "present_prev2",
        "present_prev3",
        "sum_severity_prev1",
        "sum_severity_prev2",
        "sum_severity_prev3",
        "percnt_true_prev1",
        "percnt_true_prev2",
        "percnt_true_prev3",
        "median_prev1",
        "median_prev2",
        "median_prev3",
        "severity_prev1",
        "severity_prev2",
        "severity_prev3",
        "severity_in_neighbor",
        "ergot_present_in_q1",
        "ergot_present_in_q2",
        "ergot_present_in_q3",
        "ergot_present_in_q4",
        "sum_severity_in_q1",
        "sum_severity_in_q2",
        "sum_severity_in_q3",
        "sum_severity_in_q4",
    ]

    def rmErgotPredictors(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = df.columns.tolist()
        toRemove = []

        for col in cols:
            if col in SetModifier.ERGOT_PREDICTORS:
                toRemove.append(str(col))

        return df.drop(columns=toRemove)

    def rmErgotFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = df.columns.tolist()
        toRemove = []

        for col in cols:
            if col in SetModifier.ERGOT_FEATURES:
                toRemove.append(str(col))

        return df.drop(columns=toRemove)

    def InputeData(self, df, strat):
        cols = df.columns.tolist()
        replacements = []

        if strat == "mean" or strat == "median" or strat == "mode" or strat == "zero":
            if strat == "mean":
                replacements = df.mean(axis=0, skipna=True)
            elif strat == "median":
                replacements = df.median(axis=0, skipna=True)
            elif strat == "mode":
                replacements = df.mode(axis=0, skipna=True)
            elif strat == "zero":
                replacements = [0] * (len(cols))

            for index, col in enumerate(cols):
                df[col].fillna(replacements[index], inplace=True)

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

                logData = np.log(df[col]).replace(-math.inf, 0)
                sqrtData = np.sqrt(df[col]).replace(-math.inf, 0)
                cbrtRoot = np.cbrt(df[col]).replace(-math.inf, 0)

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
        scaledValues = scaler.fit_transform(df)

        return pd.DataFrame(scaledValues, columns=df.columns, index=df.index)

    def useStandardScaler(self, df):
        scaler = StandardScaler()
        scaledValues = scaler.fit_transform(df)

        return pd.DataFrame(scaledValues, columns=df.columns, index=df.index)

    def randomSplit(
        self, df: pd.DataFrame, testSize: float = 0.2, randomSeed: int = 42
    ) -> dict:
        train_set, test_set = train_test_split(
            df, test_size=testSize, random_state=randomSeed
        )

        return {"train": train_set, "test": test_set}

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

        return {"train": train_set, "test": test_set}
