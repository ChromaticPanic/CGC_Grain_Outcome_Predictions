import pandas as pd
import sqlalchemy as sq

class DataHandler:
    def pushData(df: pd.DataFrame, prov, conn) -> None:
        tablename = f'{prov.lower()}_station_data'
        df.to_sql(tablename, conn, if_exists="append", index=False)

    def processData(df: pd.DataFrame, stationID: str) -> None:
        try:
            df.drop(columns=['Data Quality', 'Max Temp Flag', 'Mean Temp Flag', 'Min Temp Flag', 'Heat Deg Days Flag', 'Cool Deg Days Flag', 'Spd of Max Gust (km/h)',
                            'Total Rain Flag', 'Total Snow Flag', 'Total Precip Flag', 'Snow on Grnd Flag', 'Dir of Max Gust Flag', 'Spd of Max Gust Flag',
                            'Heat Deg Days (°C)', 'Cool Deg Days (°C)', 'Longitude (x)', 'Latitude (y)', 'Dir of Max Gust (10s deg)'], inplace=True)
        except:
            df.to_csv("data/failed/" + str(df.iloc[0, 0]) + "_unexpected_column_names.csv", index=False)

        # replace all station names with stationIDs
        df['Station Name'] = stationID

        # Climate ID	Date/Time	Year	Month	Day	Max Temp (Â°C)	Min Temp (Â°C)	Mean Temp (Â°C)	Total Rain (mm)	Total Snow (cm)	Total Precip (mm)	Snow on Grnd (cm)	Dir of Max Gust (10s deg)	Spd of Max Gust (km/h)
        # ClimateID Date Year Month Day MaxTemp MinTemp MeanTemp TotalRain TotalSnow TotalPrecip SnowOnGrnd DirOfMaxGust SpdOfMaxGust
        df.rename(columns={df.columns[0]: "station_id"}, inplace=True)
        df.rename(columns={df.columns[1]: "date"}, inplace=True)
        df.rename(columns={df.columns[2]: "year"}, inplace=True)
        df.rename(columns={df.columns[3]: "month"}, inplace=True)
        df.rename(columns={df.columns[4]: "Day"}, inplace=True)
        df.rename(columns={df.columns[5]: "max_temp"}, inplace=True)
        df.rename(columns={df.columns[6]: "min_temp"}, inplace=True)
        df.rename(columns={df.columns[7]: "mean_temp"}, inplace=True)
        df.rename(columns={df.columns[8]: "total_rain"}, inplace=True)
        df.rename(columns={df.columns[9]: "total_snow"}, inplace=True)
        df.rename(columns={df.columns[10]: "total_precip"}, inplace=True)
        df.rename(columns={df.columns[11]: "snow_on_grnd"}, inplace=True)

        df.dropna(subset=['MeanTemp'], inplace=True)
        df.loc[df['SnowOnGrnd'].isnull(), 'SnowOnGrnd'] = 0
        df.loc[df['TotalRain'].isnull(), 'TotalRain'] = 0
        df.loc[df['TotalSnow'].isnull(), 'TotalSnow'] = 0
        df.loc[df['TotalPrecip'].isnull(), 'TotalPrecip'] = 0
        
        df['MaxTemp'] = np.where(df['MaxTemp'].isnull(), df['MeanTemp'], df['MaxTemp'])
        df['MinTemp'] = np.where(df['MinTemp'].isnull(), df['MeanTemp'], df['MinTemp'])

        df[['ClimateID', 'Date']] = df[['ClimateID', 'Date']].astype(str)
        df[['Year', 'Month', 'Day']] = df[['Year', 'Month', 'Day']].astype(int)
        df[['MaxTemp', 'MinTemp', 'MeanTemp', 'TotalRain', 'TotalSnow', 'TotalPrecip', 'SnowOnGrnd']] = df[[
            'MaxTemp', 'MinTemp', 'MeanTemp', 'TotalRain', 'TotalSnow', 'TotalPrecip', 'SnowOnGrnd']].astype(sq.Date())

        return df