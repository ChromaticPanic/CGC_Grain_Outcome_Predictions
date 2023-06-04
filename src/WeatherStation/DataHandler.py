import pandas as pd
import sqlalchemy as sq
import numpy as np

class DataHandler:
    def pushData(self, df: pd.DataFrame, prov, conn) -> None:
        tablename = f'{prov.lower()}_station_data'
        df.to_sql(tablename, conn, schema='public', if_exists="append", index=False)

        print(df["date"].max())
        # print(stored x number of updates with the latest date of _____)
        return df["date"].max()

    def processData(self, df: pd.DataFrame, stationID: str, lastUpdated) -> None:
        try:
            df.drop(columns=['Data Quality', 'Max Temp Flag', 'Mean Temp Flag', 'Min Temp Flag', 'Heat Deg Days Flag', 'Cool Deg Days Flag', 'Spd of Max Gust (km/h)',
                            'Total Rain Flag', 'Total Snow Flag', 'Total Precip Flag', 'Snow on Grnd Flag', 'Dir of Max Gust Flag', 'Spd of Max Gust Flag',
                            'Heat Deg Days (°C)', 'Cool Deg Days (°C)', 'Longitude (x)', 'Station Name', 'Latitude (y)', 'Dir of Max Gust (10s deg)'], inplace=True)
        except:
            df.to_csv("data/failed/" + str(df.iloc[0, 0]) + "_unexpected_column_names.csv", index=False)

        # Climate ID	Date/Time	Year	Month	Day	Max Temp (Â°C)	Min Temp (Â°C)	Mean Temp (Â°C)	Total Rain (mm)	Total Snow (cm)	Total Precip (mm)	Snow on Grnd (cm)	Dir of Max Gust (10s deg)	Spd of Max Gust (km/h)
        # ClimateID Date Year Month Day MaxTemp MinTemp MeanTemp TotalRain TotalSnow TotalPrecip SnowOnGrnd DirOfMaxGust SpdOfMaxGust
        df.rename(columns={df.columns[0]: "station_id"}, inplace=True)
        df.rename(columns={df.columns[1]: "date"}, inplace=True)
        df.rename(columns={df.columns[2]: "year"}, inplace=True)
        df.rename(columns={df.columns[3]: "month"}, inplace=True)
        df.rename(columns={df.columns[4]: "day"}, inplace=True)
        df.rename(columns={df.columns[5]: "max_temp"}, inplace=True)
        df.rename(columns={df.columns[6]: "min_temp"}, inplace=True)
        df.rename(columns={df.columns[7]: "mean_temp"}, inplace=True)
        df.rename(columns={df.columns[8]: "total_rain"}, inplace=True)
        df.rename(columns={df.columns[9]: "total_snow"}, inplace=True)
        df.rename(columns={df.columns[10]: "total_precip"}, inplace=True)
        df.rename(columns={df.columns[11]: "snow_on_grnd"}, inplace=True)

        print(df)

        df[['station_id']] = df[['station_id']].astype(str)
        df[['date']] = df[['date']].astype('datetime64[ns]')
        df[['year', 'month', 'day']] = df[['year', 'month', 'day']].astype(int)
        df[['max_temp', 'min_temp', 'mean_temp', 'total_rain', 'total_snow', 'total_precip', 'snow_on_grnd']] = df[[
            'max_temp', 'min_temp', 'mean_temp', 'total_rain', 'total_snow', 'total_precip', 'snow_on_grnd']].astype(float)

        # remove the ones we've already stored as per our last update
        print(type(lastUpdated))
        print(type(df.date[0]))

        df.drop(df[df.date <= lastUpdated].index, inplace=True)
        print('yes')

        df.dropna(subset=['mean_temp'], inplace=True)
        df.loc[df['snow_on_grnd'].isnull(), 'snow_on_grnd'] = 0
        df.loc[df['total_rain'].isnull(), 'total_rain'] = 0
        df.loc[df['total_snow'].isnull(), 'total_snow'] = 0
        df.loc[df['total_precip'].isnull(), 'total_precip'] = 0
        
        df['max_temp'] = np.where(df['max_temp'].isnull(), df['mean_temp'], df['max_temp'])
        df['min_temp'] = np.where(df['min_temp'].isnull(), df['mean_temp'], df['min_temp'])

        return df