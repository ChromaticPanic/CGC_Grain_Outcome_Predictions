
import pandas as pd
import typing

def scaleColumns(df: pd.DataFrame, cols: typing.List[str], scaler: typing.Callable) -> pd.DataFrame:
    """
    Scale the columns of a dataframe using a scaler function

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to scale
    cols : typing.List[str]
        List of columns to scale
    scaler : typing.Callable
        Scaler function to use

    Returns
    -------
    pd.DataFrame
        Scaled dataframe
    """
    for col in cols:
        df[col] = df[col].astype(float)
        df[col] = scaler(df[col])
    return df

