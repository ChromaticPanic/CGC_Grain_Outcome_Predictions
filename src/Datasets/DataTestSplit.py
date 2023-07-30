# -------------------------------------------
# DataTestSplit.py
#
# After loading any dataset, this class can be used to split the dataset into multiple train and test sets
# -------------------------------------------
from sklearn.model_selection import train_test_split  # type: ignore
from typing import Optional, Tuple
import pandas as pd


def splitDataPivot(
    df: pd.DataFrame, drop_features: Optional[list], target_variable: str
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Purpose: preprocessing to split a set into its data (X) and target (Y)

    Psuedocode:
    - Drop irrelevant targets
    - Split the data (X) and the target data (Y)
    """
    if drop_features == None:
        drop_features = []

        if target_variable in drop_features:
            drop_features.remove(target_variable)

        if "year" in drop_features:
            drop_features.remove("year")

    df.drop(columns=drop_features, inplace=True)
    X = df.drop(columns=[target_variable])
    y = df[target_variable]

    return X, y


def splitData(
    df: pd.DataFrame,
    drop_features: Optional[list],
    target_variable: str,
    pivot: int = 2019,
    val_size: float = 0.2,
    stratified: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series,]:
    """
    Purpose:
    Splits the data equally into different sets based on the target column and its possible values

    Psuedocode: 
    - Take the data before a specific year and set it as the training data
    - Take the data after a specific year and set it as the testing data
    - Drop irrelevant data
    - Seperate data (X) from the target Data (Y)
    - Split the sets into multiple subsets (kfolds)
        - [random](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html) 
        - [stratified](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
    """

    # train set
    df_train = df[df["year"] < pivot]  # all data before PIVOT
    X_train_df, y_train_df = splitDataPivot(
        df_train, drop_features=drop_features, target_variable=target_variable
    )  # split data into X_train_df and y_train_df

    # test set
    df_test = df[df["year"] >= pivot]  # all data after and including PIVOT
    X_test, y_test = splitDataPivot(
        df_test, drop_features=drop_features, target_variable=target_variable
    )

    # now train test for validation
    if stratified:
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_df,
            y_train_df,
            test_size=val_size,
            random_state=42,
            stratify=y_train_df,
        )
    else:
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_df, y_train_df, test_size=val_size, random_state=42
        )

    return X_train, X_val, X_test, y_train, y_val, y_test
