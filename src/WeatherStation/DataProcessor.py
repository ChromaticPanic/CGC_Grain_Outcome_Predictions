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
    
    def dataProcessHourly(self, df: pandas.DataFrame, lastUpdated: numpy.datetime64) -> pandas.DataFrame:
        NULLFLAG = -9999
        try:
            # discard	discard	discard	keep	discard	discard	keep	keep	keep	keep	keep	keep	discard	keep	discard	discard	discard	keep	discard	keep	discard	keep	discard	discard	discard	keep	discard	keep	discard	keep	discard	
            # x	y	STATION_NAME	CLIMATE_IDENTIFIER	ID	LOCAL_DATE	PROVINCE_CODE	LOCAL_YEAR	LOCAL_MONTH	LOCAL_DAY	LOCAL_HOUR	TEMP	TEMP_FLAG	DEW_POINT_TEMP	DEW_POINT_TEMP_FLAG	HUMIDEX	HUMIDEX_FLAG	PRECIP_AMOUNT	PRECIP_AMOUNT_FLAG	RELATIVE_HUMIDITY	RELATIVE_HUMIDITY_FLAG	STATION_PRESSURE	STATION_PRESSURE_FLAG	VISIBILITY	VISIBILITY_FLAG	WINDCHILL	WINDCHILL_FLAG	WIND_DIRECTION	WIND_DIRECTION_FLAG	WIND_SPEED	WIND_SPEED_FLAG	

            df.drop(columns=['x', 'y', 'STATION_NAME', 'ID', 'LOCAL_DATE', 'TEMP_FLAG', 'DEW_POINT_TEMP_FLAG', 'HUMIDEX', 'HUMIDEX_FLAG', 'PRECIP_AMOUNT_FLAG', 'RELATIVE_HUMIDITY_FLAG', 'STATION_PRESSURE_FLAG', 'VISIBILITY', 'VISIBILITY_FLAG', 'WINDCHILL_FLAG', 'WIND_DIRECTION_FLAG', 'WIND_SPEED_FLAG'], inplace=True)
        except:
            df.to_csv("Failed/" + str(df.iloc[0, 0]) +
                    "_unexpected_column_names.csv", index=False)

        expList = ['CLIMATE_IDENTIFIER', 'PROVINCE_CODE', 'LOCAL_YEAR', 'LOCAL_MONTH', 'LOCAL_DAY', 'LOCAL_HOUR', 'TEMP', 'DEW_POINT_TEMP', 'PRECIP_AMOUNT', 'RELATIVE_HUMIDITY', 'STATION_PRESSURE', 'WINDCHILL', 'WIND_DIRECTION', 'WIND_SPEED']
        currList = list(df.columns.values)
        
        if self.validateColumnNames(currList, expList):
            df.rename(columns={df.columns[0]: "ClimateID"}, inplace=True)
            df.rename(columns={df.columns[1]: "ProvinceCode"}, inplace=True)
            df.rename(columns={df.columns[2]: "Year"}, inplace=True)
            df.rename(columns={df.columns[3]: "Month"}, inplace=True)
            df.rename(columns={df.columns[4]: "Day"}, inplace=True)
            df.rename(columns={df.columns[5]: "Hour"}, inplace=True)
            df.rename(columns={df.columns[6]: "Temp"}, inplace=True)
            df.rename(columns={df.columns[7]: "DewPointTemp"}, inplace=True)
            df.rename(columns={df.columns[8]: "PrecipAmount"}, inplace=True)
            df.rename(columns={df.columns[9]: "RelativeHumidity"}, inplace=True)
            df.rename(columns={df.columns[10]: "StationPressure"}, inplace=True)
            df.rename(columns={df.columns[11]: "WindChill"}, inplace=True)
            df.rename(columns={df.columns[12]: "WindDirection"}, inplace=True)
            df.rename(columns={df.columns[13]: "WindSpeed"}, inplace=True)

            # df.dropna(subset=['Temp'], inplace=True)
            df.loc[df['Temp'].isnull(), 'Temp'] = NULLFLAG
            df.loc[df['DewPointTemp'].isnull(), 'DewPointTemp'] = NULLFLAG
            df.loc[df['PrecipAmount'].isnull(), 'PrecipAmount'] = NULLFLAG
            df.loc[df['RelativeHumidity'].isnull(), 'RelativeHumidity'] = NULLFLAG
            df.loc[df['StationPressure'].isnull(), 'StationPressure'] = NULLFLAG
            df.loc[df['WindChill'].isnull(), 'WindChill'] = NULLFLAG
            df.loc[df['WindDirection'].isnull(), 'WindDirection'] = NULLFLAG
            df.loc[df['WindSpeed'].isnull(), 'WindSpeed'] = NULLFLAG

            df[['ClimateID', 'ProvinceCode']] = df[['ClimateID', 'ProvinceCode']].astype(str)
            df[['Year', 'Month', 'Day', 'Hour']] = df[['Year', 'Month', 'Day', 'Hour']].astype(int)
            df[['Temp', 'DewPointTemp', 'PrecipAmount', 'RelativeHumidity', 'StationPressure', 'WindChill', 'WindDirection', 'WindSpeed']] = df[['Temp', 
                        'DewPointTemp', 'PrecipAmount', 'RelativeHumidity', 'StationPressure', 'WindChill', 'WindDirection', 'WindSpeed']].astype(float)

            self.removeOlderThan(df, lastUpdated)
            # we try a db push, but if it fails, we place the data in a csv file
            # try:
            push_data(df, "WeatherDataHourlyTwentyYear")
            # db_con.execute(
            #     "UPDATE public.\"TenYrStationsHourly\" SET \"dataAvailable\" = True WHERE \"ClimateID\" like CAST(\'{}\' AS TEXT);".format(stationID))
            # except:
            #     df.to_csv("Failed/" + str(df.iloc[0, 0]) +
            #             "_data_failed_dbpush.csv", index=False)
        else:
            df.to_csv("Failed/" + str(df.iloc[0, 0]) +
                    "_error_column_names.csv", index=False)
            
    def validateColumnNames(self, curr: list, exp: list) -> bool:
        for name in curr:
            if name not in exp:
                return False
        return True