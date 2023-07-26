
import pandas as pd
from typing import List, Optional
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
