
import pandas as pd
from typing import List, Optional, Tuple
from sklearn.preprocessing import (
    MaxAbsScaler,
    MinMaxScaler,
    Normalizer,
    PowerTransformer,
    QuantileTransformer,
    RobustScaler,
    StandardScaler,
    OneHotEncoder,
    minmax_scale,
)
from imblearn.over_sampling import (
    RandomOverSampler,
    SMOTE,
    ADASYN,
    BorderlineSMOTE,
    KMeansSMOTE,
    SVMSMOTE,
    SMOTENC,
    SMOTEN,
)
from imblearn.under_sampling import (
    RandomUnderSampler,
    ClusterCentroids,
    CondensedNearestNeighbour,
    EditedNearestNeighbours,
    RepeatedEditedNearestNeighbours,
    AllKNN,
    InstanceHardnessThreshold,
    NearMiss,
    NeighbourhoodCleaningRule,
    OneSidedSelection,
    TomekLinks
)
from imblearn.combine import (
    SMOTEENN,
    SMOTETomek
)

from Shared.DataService import DataService
from dotenv import load_dotenv
import os


def getConn(envpath: str = ".env"):
    load_dotenv(envpath)
    PG_DB = os.getenv("POSTGRES_DB")
    PG_ADDR = os.getenv("POSTGRES_ADDR")
    PG_PORT = os.getenv("POSTGRES_PORT")
    PG_USER = os.getenv("POSTGRES_USER")
    PG_PW = os.getenv("POSTGRES_PW")

    if (
        PG_DB is None
        or PG_ADDR is None
        or PG_PORT is None
        or PG_USER is None
        or PG_PW is None
    ):
        raise Exception("Missing required env var(s)")
    db = DataService(PG_DB, PG_ADDR, int(PG_PORT), PG_USER, PG_PW)

    return db.connect()

def scaleColumns(df: pd.DataFrame, cols: List[str], options: Optional[object] = None, scalingMethod: Optional[int] = 0) -> pd.DataFrame:
    """Scale the columns of a dataframe using a scaler.

    Args:
        df (pd.DataFrame): The dataframe to scale.
        cols (typing.List[str]): The columns to scale.
        scaler (int): The scaler to use.

    Returns:
        pd.DataFrame: The scaled dataframe.
    """
    
    scaler = MinMaxScaler(options)
    if scalingMethod == 1:
        scaler = MaxAbsScaler(options)
    elif scalingMethod == 2:
        scaler = StandardScaler(options)
    elif scalingMethod == 3:
        scaler = RobustScaler(options)
    elif scalingMethod == 4:
        scaler = Normalizer(options)
    elif scalingMethod == 5:
        scaler = PowerTransformer(options)
    elif scalingMethod == 6:
        scaler = QuantileTransformer(options)

    for col in cols:
        df[col] = scaler.fit_transform(df[col].values.reshape(-1, 1)) # not sure if correct

    return df

def encodeColumns(df: pd.DataFrame, cols: List[str], options: Optional[object] = None) -> pd.DataFrame:
    """Encode the columns of a dataframe using a one-hot encoder.

    Args:
        df (pd.DataFrame): The dataframe to encode.
        cols (typing.List[str]): The columns to encode.

    Returns:
        pd.DataFrame: The encoded dataframe.
    """
    
    encoder = OneHotEncoder(options)

    for col in cols:
        df[col] = encoder.fit_transform(df[col].values.reshape(-1, 1)) # not sure if correct

    return df


def extractYears(df: pd.DataFrame, year: int, yearEnd: Optional[int] = None) -> pd.DataFrame:
    """Extract the rows of a dataframe that correspond to a given year.

    Args:
        df (pd.DataFrame): The dataframe to extract from.
        year (int): The year to extract.
        yearEnd (int, optional): The end year to extract. Defaults to None.

    Returns:
        pd.DataFrame: The extracted dataframe.
    """
    
    if yearEnd is None:
        return df.loc[df["year"] == year]
    else:
        return df.loc[(df["year"] >= year) & (df["year"] <= yearEnd)]
    

