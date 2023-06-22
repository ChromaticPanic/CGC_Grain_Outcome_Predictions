import os
import pandas as pd
import numpy as np
import pandas as pd
import sqlalchemy as sq
from dotenv import load_dotenv
from DataService import DataService
from ClimateDataRequester import ClimateDataRequester as cdr

os.chdir("/data")
load_dotenv("docker/.env")
PGUSER = os.getenv("POSTGRES_USER")
PGPW = os.getenv("POSTGRES_PW")
PGDB = os.getenv("POSTGRES_DB")


def push_data(df: pd.DataFrame) -> None:
    dataService = DataService(PGDB, PGUSER, PGPW)
    db_con = dataService.connect()
    df.to_sql("WeatherData", db_con, if_exists="append", index=False)
    dataService.cleanup()


def dataProcessA(df: pd.DataFrame, stationID: str) -> None:
    dataService = DataService(PGDB, PGUSER, PGPW)
    db_con = dataService.connect()
    try:
        df.drop(
            columns=[
                "Data Quality",
                "Max Temp Flag",
                "Mean Temp Flag",
                "Min Temp Flag",
                "Heat Deg Days Flag",
                "Cool Deg Days Flag",
                "Spd of Max Gust (km/h)",
                "Total Rain Flag",
                "Total Snow Flag",
                "Total Precip Flag",
                "Snow on Grnd Flag",
                "Dir of Max Gust Flag",
                "Spd of Max Gust Flag",
                "Heat Deg Days (°C)",
                "Cool Deg Days (°C)",
                "Longitude (x)",
                "Latitude (y)",
                "Station Name",
                "Dir of Max Gust (10s deg)",
            ],
            inplace=True,
        )
    except:
        df.to_csv(
            "data/failed/" + str(df.iloc[0, 0]) + "_unexpected_column_names.csv",
            index=False,
        )

    # Climate ID	Date/Time	Year	Month	Day	Max Temp (Â°C)	Min Temp (Â°C)	Mean Temp (Â°C)	Total Rain (mm)	Total Snow (cm)	Total Precip (mm)	Snow on Grnd (cm)	Dir of Max Gust (10s deg)	Spd of Max Gust (km/h)
    # ClimateID Date Year Month Day MaxTemp MinTemp MeanTemp TotalRain TotalSnow TotalPrecip SnowOnGrnd DirOfMaxGust SpdOfMaxGust
    df.rename(columns={df.columns[0]: "ClimateID"}, inplace=True)
    df.rename(columns={df.columns[1]: "Date"}, inplace=True)
    df.rename(columns={df.columns[2]: "Year"}, inplace=True)
    df.rename(columns={df.columns[3]: "Month"}, inplace=True)
    df.rename(columns={df.columns[4]: "Day"}, inplace=True)
    df.rename(columns={df.columns[5]: "MaxTemp"}, inplace=True)
    df.rename(columns={df.columns[6]: "MinTemp"}, inplace=True)
    df.rename(columns={df.columns[7]: "MeanTemp"}, inplace=True)
    df.rename(columns={df.columns[8]: "TotalRain"}, inplace=True)
    df.rename(columns={df.columns[9]: "TotalSnow"}, inplace=True)
    df.rename(columns={df.columns[10]: "TotalPrecip"}, inplace=True)
    df.rename(columns={df.columns[11]: "SnowOnGrnd"}, inplace=True)

    df.dropna(subset=["MeanTemp"], inplace=True)
    df.loc[df["SnowOnGrnd"].isnull(), "SnowOnGrnd"] = 0
    df.loc[df["TotalRain"].isnull(), "TotalRain"] = 0
    df.loc[df["TotalSnow"].isnull(), "TotalSnow"] = 0
    df.loc[df["TotalPrecip"].isnull(), "TotalPrecip"] = 0
    df["MaxTemp"] = np.where(df["MaxTemp"].isnull(), df["MeanTemp"], df["MaxTemp"])
    df["MinTemp"] = np.where(df["MinTemp"].isnull(), df["MeanTemp"], df["MinTemp"])

    df[["ClimateID", "Date"]] = df[["ClimateID", "Date"]].astype(str)
    df[["Year", "Month", "Day"]] = df[["Year", "Month", "Day"]].astype(int)
    df[
        [
            "MaxTemp",
            "MinTemp",
            "MeanTemp",
            "TotalRain",
            "TotalSnow",
            "TotalPrecip",
            "SnowOnGrnd",
        ]
    ] = df[
        [
            "MaxTemp",
            "MinTemp",
            "MeanTemp",
            "TotalRain",
            "TotalSnow",
            "TotalPrecip",
            "SnowOnGrnd",
        ]
    ].astype(
        float
    )

    # we try a db push, but if it fails, we place the data in a csv file
    # try:
    push_data(df)
    query = sq.text(
        'UPDATE public."StationsDly" SET "scraped" = True WHERE "Climate ID" like CAST(\'{}\' AS TEXT);'.format(
            stationID
        )
    )
    db_con.execute(query)
    # except:
    #     df.to_csv("Failed/" + str(df.iloc[0, 0]) +
    #             "_data_failed_dbpush.csv", index=False)
    dataService.cleanup()
