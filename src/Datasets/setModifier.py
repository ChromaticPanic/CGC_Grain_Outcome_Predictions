# -------------------------------------------
# setModifier.py
#
# After loading any dataset, this class can be used to make quick adjustments to the data
#
# Remarks:
#   - As is, the function attemptBellCurve needs to be adjusted to handle negative values better
#   - As is rmErgotPredictors should be adjusted to also remove any current year (relative to predictions) data
#   - Both ERGOT_PREDICTORS and ERGOT_FEATURES (class constants) may need to be manually changed as the ergot data changes
# -------------------------------------------
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn.preprocessing import MinMaxScaler  # type: ignore
from sklearn.random_projection import GaussianRandomProjection  # type: ignore
from sklearn.decomposition import PCA  # type: ignore
from scipy import stats  # type: ignore
from typing import List
import pandas as pd
import numpy as np
import math


class SetModifier:
    # A list of the Ergot predictors (used to remove features without the need to load any datasets)
    ERGOT_PREDICTORS = [
        "percnt_true",
        "sum_severity",
        "ergot_present_in_q3",
        "ergot_present_in_q4",
        "sum_severity_in_q3",
        "sum_severity_in_q4",
    ]

    # A list of the Ergot features (used to remove features without the need to load any datasets)
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
        """
        Purpose:
        Removes the ergot predictors from the dataset (as they may provide the model with information that should be unknown at the time)

        Pseudocode:
        - Get the list of columns present in the DataFrame
        - For each column check if its a predictor
        - If it is, add it the list of columns to remove
        - [Drop all columns found](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html)
        """
        cols = df.columns.tolist()
        toRemove = []

        for col in cols:
            if col in SetModifier.ERGOT_PREDICTORS:
                toRemove.append(str(col))

        return df.drop(columns=toRemove)

    def rmErgotFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Purpose:
        Removes the ergot features from the dataset

        Pseudocode:
        - Get the list of columns present in the DataFrame
        - For each column check if its a ergot feature
        - If it is, add it the list of columns to remove
        - [Drop all columns found](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html)
        """
        cols = df.columns.tolist()
        toRemove = []

        for col in cols:
            if col in SetModifier.ERGOT_FEATURES:
                toRemove.append(str(col))

        return df.drop(columns=toRemove)

    def InputeData(self, df: pd.DataFrame, strat: str) -> pd.DataFrame:
        """
        Purpose:
        Replace undesirable values, different strategies include;
        mean, median, mode and zero values

        Pseudocode:
        - Get the column names from the provided DataFrame
        - Determine which strategy was selected if any
        - For whichever strategy was provided, compute the replacement values for each column and return them as a list
        - Iterate through each column, replacing any values that arent numbers (using the calculated replacements)

        Functions used:
        - [mean](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.mean.html)
        - [median](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.median.html)
        - [mode](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.mode.html)
        - [fillna](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html)

        Remarks: although scikit learn has an impute function, from my experience it often failed
        This function can be found here: https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
        """
        cols = df.columns.tolist()
        replacements: List[float] = []

        if strat == "mean" or strat == "median" or strat == "mode" or strat == "zero":
            if strat == "mean":
                replacements = df.mean(axis=0, skipna=True).tolist()
            elif strat == "median":
                replacements = df.median(axis=0, skipna=True).tolist()
            elif strat == "mode":
                replacements = df.mode(axis=0, skipna=True).tolist()
            elif strat == "zero":
                replacements = [0] * (len(cols))  # creates a list full of zeros

            # For each column, replace non numbers by the calculated replacements
            for index, col in enumerate(cols):
                # This edge case occurs when no valid values appear inside the entire column
                # in other words, there are no values we can use to compute a replacement from
                if np.isnan(replacements[index]):
                    replacements[index] = 0

                df[col].fillna(replacements[index], inplace=True)

        return df

    def attemptBellCurve(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Purpose:
        Models prefer bell curve distributions, therefore this function attempts to scale data to achieve this

        Pseudocode:
        - Get the list of columns from the DataFrame provided
        - For each column calculate the p value (p values less than or equal to 0.05 mean the data is PROBABLY not in the shape of a bell curve)
        - Scale the entire column using the log function
        - Scale the entire column using the square root function
        - Scale the entire column using the cube root function
        - Negative values cause errors, therefore we attempt to remove them (this is not a good approach and often results in errors)
        - Check the p values for the scaled columns
        - If we get a better p-value from any of our scaling data sets, use that data instead

        Functions used:
        - [shapiro](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html)
        - [log](https://numpy.org/doc/stable/reference/generated/numpy.log.html)
        - [sqrt](https://numpy.org/doc/stable/reference/generated/numpy.sqrt.html)
        - [cbrt](https://numpy.org/doc/stable/reference/generated/numpy.cbrt.html)

        Remarks: This function needs to be adjusted to handle negative values better
        """
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

    def useMinMaxScaler(
        self, df: pd.DataFrame, forNeuralNetwork: bool = False
    ) -> pd.DataFrame:
        """
        Purpose:
        Models prefer data within consistant ranges (otherwise some values may impact results more then others)
        This function scales all values into a consistantly small range

        Pseudocode:
        - [Create the scaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html)
        - Scale the values (this returns a multi-dimensional array)
        - Fit the data back into a DataFrame with the original columns and indexs

        Remarks: Neural networks prefer working with values close to 0, therefore MinMaxScalar will set the range from -1 and 1 for neural networks
        and 0 and 1 for all other datasets (as per the forNeuralNetwork boolean flag)
        """
        scaler = (
            MinMaxScaler(feature_range=(-1, 1))
            if forNeuralNetwork
            else MinMaxScaler(feature_range=(0, 1))
        )

        scaledValues = scaler.fit_transform(df)

        return pd.DataFrame(scaledValues, columns=df.columns, index=df.index)

    def useStandardScaler(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Purpose:
        Models prefer data within more consistant ranges (otherwise some values may impact results more then others)
        This function standardizes the data, however, there is no set range used in the scaling process

        Pseudocode:
        - [Create the scaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
        - Use the scaler (this returns a multi-dimensional array)
        - Fit the data back into a DataFrame with the original columns and indexs

        Remarks: This method of scaling is much less affected by outliers
        """
        scaler = StandardScaler()
        scaledValues = scaler.fit_transform(df)

        return pd.DataFrame(scaledValues, columns=df.columns, index=df.index)

    def randomSplit(
        self, df: pd.DataFrame, testSize: float = 0.2, randomSeed: int = 42
    ) -> dict:
        """
        Purpose:
        Splits the data randomly into different sets

        Pseudocode:
        - [Split the dataset](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
        - Return the data as a dictionary:
            - "train" holds 80% of the data (unless a different testSize is provided)
            - "test" holds 20% of the data (unless a different testSize is provided)
        """
        train_set, test_set = train_test_split(
            df, test_size=testSize, random_state=randomSeed
        )

        return {"train": train_set, "test": test_set}

    def stratifiedSplit(
        self,
        df: pd.DataFrame,
        descrimCol,
        testSize: float = 0.2,
        randomSeed: int = 42,
    ) -> dict:
        """
        Purpose:
        Splits the data equally into different sets based on a column and its possible values

        Pseudocode:
        - [Split the dataset](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
        - Return the data as a dictionary:
            - "train" holds 80% of the data (unless a different testSize is provided)
            - "test" holds 20% of the data (unless a different testSize is provided)
        """
        train_set, test_set = train_test_split(
            df, stratify=descrimCol, test_size=testSize, random_state=randomSeed
        )

        return {"train": train_set, "test": test_set}

    def usePCAReduction(self, dataset: pd.DataFrame) -> np.ndarray:
        """
        Purpose:
        Reduce the number of attributes whilst maintaining most of the datas variance

        Functions used:
        - [PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)

        Remarks:
        - This does not ensure better performance
        - This function creates entirely new attributes
        """
        pca = PCA()
        pca.fit_transform(dataset)

        return pca

    def useGausReduction(
        self, dataset: pd.DataFrame, num_components: int = 25
    ) -> np.ndarray:
        """
        Purpose:
        Reduce the number of attributes by projecting random attributes onto the plane of others

        Functions used:
        - [GaussianRandomProjection](https://scikit-learn.org/stable/modules/generated/sklearn.random_projection.GaussianRandomProjection.html)

        Remarks:
        - This does not ensure better performance
        - This function creates entirely new attributes
        """
        gaussian_rnd_proj = GaussianRandomProjection(
            random_state=0, n_components=num_components
        )

        X_reduced = gaussian_rnd_proj.fit_transform(dataset)

        return X_reduced
