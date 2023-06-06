# ----------------------------------------------------
# DataProcessor.py
#
# Purpose: handles the more complex data processing and manipulations for ScrapeStations.py 
# ----------------------------------------------------
from datetime import datetime
import numpy, pandas, typing


class DataProcessor:
    def removeInactive(self, stations: pandas.DataFrame, states: list({str, numpy.datetime64, bool})) -> pandas.DataFrame:
        for state in states:
            if not state['is_active']:
                stations.drop(stations[stations.station_id == state['station_id']].index, inplace=True)

        return stations

    def addLastUpdated(self, stations: str, states: list({str, numpy.datetime64, bool})) -> pandas.DataFrame:
        stations['last_updated'] = None

        for state in states:
            stations.loc[stations['station_id'] == state['station_id'], 'last_updated'] = state['last_updated']

        return stations

    def findLatestDate(self, listOfDates: list) -> numpy.datetime64:
        validDates = []     # Holds the list of valid dates
        latestDate = None   # Holds the latest date, defaults to None if no valid dates are given
        
        if len(listOfDates) > 0:
            for date in listOfDates:
                if not numpy.isnat(numpy.datetime64(date)): # Numpy evaluates each date (casting is necessairy even if casted previously) 
                    validDates.append(date)
            
            if validDates:
                latestDate = max(validDates)

        return latestDate

    def calcDateRange(self, firstYearWithData: int, lastUpdated: numpy.datetime64, lastYearWithData: int, currentYear: int=datetime.now().year) -> typing.Tuple[int, int]:
        maxYear = min(lastYearWithData, currentYear)    # Pull to the current year or whatever year the data goes up until (if either are None throws error)
        minYear = firstYearWithData                     # Whenever the station started collecting data
        
        if not numpy.isnat(numpy.datetime64(lastUpdated)):  # Confirms the pulled year is a valid datetime (numpy)
            lastUpdated = pandas.to_datetime(lastUpdated)

            if lastUpdated.year > firstYearWithData:
                minYear = lastUpdated.year

        return minYear, maxYear

    def removeOlderThan(self, df: pandas.DataFrame, lastUpdated: numpy.datetime64):
        if lastUpdated:
            df.drop(df[df.date <= lastUpdated].index, inplace=True) # Drops old/duplicate data (as per the date of the previous update - lastUpdated)

    def processData(self, df: pandas.DataFrame, lastUpdated: numpy.datetime64) -> pandas.DataFrame:
        try:
            df.drop(columns=['Data Quality', 'Max Temp Flag', 'Mean Temp Flag', 'Min Temp Flag', 'Heat Deg Days Flag', 'Cool Deg Days Flag', 'Spd of Max Gust (km/h)',
                            'Total Rain Flag', 'Total Snow Flag', 'Total Precip Flag', 'Snow on Grnd Flag', 'Dir of Max Gust Flag', 'Spd of Max Gust Flag',
                            'Heat Deg Days (°C)', 'Cool Deg Days (°C)', 'Longitude (x)', 'Station Name', 'Latitude (y)', 'Dir of Max Gust (10s deg)'], inplace=True)
        except:
            df.to_csv("data/failed/" + str(df.iloc[0, 0]) + "_unexpected_column_names.csv", index=False)


        df.rename(columns={df.columns[0]: "station_id"}, inplace=True)
        df.rename(columns={df.columns[1]: "date"}, inplace=True)            # (YEAR-MO-DA)
        df.rename(columns={df.columns[2]: "year"}, inplace=True)
        df.rename(columns={df.columns[3]: "month"}, inplace=True)
        df.rename(columns={df.columns[4]: "day"}, inplace=True)
        df.rename(columns={df.columns[5]: "max_temp"}, inplace=True)        # (°C)
        df.rename(columns={df.columns[6]: "min_temp"}, inplace=True)        # (°C)
        df.rename(columns={df.columns[7]: "mean_temp"}, inplace=True)       # (°C)
        df.rename(columns={df.columns[8]: "total_rain"}, inplace=True)      # (mm)
        df.rename(columns={df.columns[9]: "total_snow"}, inplace=True)      # (cm)
        df.rename(columns={df.columns[10]: "total_precip"}, inplace=True)   # (mm)
        df.rename(columns={df.columns[11]: "snow_on_grnd"}, inplace=True)   # (cm)

        df[['station_id']] = df[['station_id']].astype(str)
        df[['date']] = df[['date']].astype('datetime64[ns]')
        df[['year', 'month', 'day']] = df[['year', 'month', 'day']].astype(int)
        df[['max_temp', 'min_temp', 'mean_temp', 'total_rain', 'total_snow', 'total_precip', 'snow_on_grnd']] = df[[
            'max_temp', 'min_temp', 'mean_temp', 'total_rain', 'total_snow', 'total_precip', 'snow_on_grnd']].astype(float)

        self.removeOlderThan(df, lastUpdated)

        df.dropna(subset=['mean_temp'], inplace=True)
        df.loc[df['snow_on_grnd'].isnull(), 'snow_on_grnd'] = 0
        df.loc[df['total_rain'].isnull(), 'total_rain'] = 0
        df.loc[df['total_snow'].isnull(), 'total_snow'] = 0
        df.loc[df['total_precip'].isnull(), 'total_precip'] = 0
        
        df['max_temp'] = numpy.where(df['max_temp'].isnull(), df['mean_temp'], df['max_temp'])
        df['min_temp'] = numpy.where(df['min_temp'].isnull(), df['mean_temp'], df['min_temp'])

        return df