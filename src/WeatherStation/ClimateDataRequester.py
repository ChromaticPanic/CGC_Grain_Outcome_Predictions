# -------------------------------------------
# climateDataRequester.py 
#
# Requests data from the [Climate Data Online web service](https://dd.weather.gc.ca/climate/observations/)
#
# Typical usage example:
#   req = ClimateDataRequester()
#   dlyDF = req.get_data(stationName: str)
#   hlyDF = req.get_hourly_data(stationName: str)
# -------------------------------------------
import requests as rq
import pandas as pd
import lxml.html
import urllib3
import typing


class ClimateDataRequester:
    def __init__(self) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.apiBaseURL = "https://dd.weather.gc.ca/climate/observations/"
        self.defaultPath = "daily/csv/"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Host": "dd.weather.gc.ca",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://dd.weather.gc.ca/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
        }

    def get_hourly_data(
        self, stationID: str, startYear: int = 2022, endYear: int = 2022
    ) -> pd.DataFrame:
        """
        Purpose:
        Requests hourly data from the [Climate Data Online web service](https://dd.weather.gc.ca/climate/observations/)

        Pseudocode:
        - Load the base URL (used for downloading the data), injecting it with both the start ane end year
        - Load the URL extension (used for downloading the data)
        - Specify how much data can be read at once
        - Download data and add it to the DataFrame until it has all been downloaded
        """
        baseUrl = f"https://api.weather.gc.ca/collections/climate-hourly/items?datetime={startYear}-01-01%2000:00:00/{endYear}-12-31%2000:00:00&CLIMATE_IDENTIFIER="
        midUrl = "&sortby=PROVINCE_CODE,CLIMATE_IDENTIFIER,LOCAL_DATE&f=csv&limit=10000&startindex="
        offset = 10000  # How much information can be read in a single request

        df = pd.DataFrame()  # Creates a dataframe to load the information into
        # The current position to read data from (since each request can only contain so much information)
        currIndex = 0

        try:
            newData = pd.read_csv(baseUrl + stationID + midUrl + str(currIndex))
            while len(newData.index) > 0:
                df = pd.concat([df, newData])
                currIndex += offset

                newData = pd.read_csv(baseUrl + stationID + midUrl + str(currIndex))
        except Exception:
            pass

        return df

    def get_data(
        self, province: str, stationID: str, startYear: int = 2022, endYear: int = 2022
    ) -> pd.DataFrame:
        """
        Purpose:
        Requests daily data from the [Climate Data Online web service](https://dd.weather.gc.ca/climate/observations/)

        Psuedocode:
        - Get the list of potential daily files to download (if none exit)
        - Remove irrelevant files to download - does not fall within startYear - endYear (if none exit)
        - For each remaining URL, load the data into a list of DataFrames
        - Concatenate all DataFrames into one: https://pandas.pydata.org/docs/reference/api/pandas.concat.html
        """
        df = pd.DataFrame()

        urlList = self.get_url_list(province, stationID)
        if len(urlList) == 0:
            return df

        trimmedList = self.trim_by_date(urlList, startYear, endYear)
        if len(trimmedList) == 0:
            return df

        dfList = []
        for url in trimmedList:
            dfList.append(self.pull_data(province + "/" + url))

        df = pd.concat(dfList)
        return df

    @typing.no_type_check
    def get_url_list(self, province: str, stationID: str = "") -> list:
        """
        Purpose:
        Gets the list of potential daily files to download

        Psuedocode:
        - Loads the download html page
        - [Get the list of files that can be downloaded](lxml.html.fromstring)
        - Add each link that ends with .csv and matches the provided stationID

        Remarks: If no stationID is provided, all links that end with .csv are added
        """
        result = []

        res = rq.get(
            self.apiBaseURL + self.defaultPath + province + "/",
            headers=self.headers,
            verify=False,
        )

        if res.status_code == 200:
            tree = lxml.html.fromstring(res.text)

            for link in tree.xpath("//a/@href"):
                if link.endswith(".csv"):
                    # If no stationID was provided when the function was called, add everything
                    if not stationID:
                        result.append(link)
                    # Otherwise add only the links that correspond to the given stationID
                    elif link.find(stationID) > -1:
                        result.append(link)

        return result

    def trim_by_date(self, csvList: list, startYear: int, endYear: int) -> list:
        """
        Purpose:
        Removes irrelevant files to download (does not fall within startYear - endYear)

        Psuedocode:
        - Starting at the last item, break down the data to extract the year
        - If the year fall within the startYear - endYear range, add it
        """
        DATEPOS = 4
        result = []

        # Start at the last entry and work back down to 0 in increments of 1
        for i in range(len(csvList) - 1, -1, -1):
            item = csvList[i]
            entry = item.split("_")
            year = int(str(entry[DATEPOS])[:4])

            if year >= startYear and year <= endYear:
                result.append(item)

        return result

    def pull_data(self, url: str) -> pd.DataFrame:
        """
        Purpose:
        Given a csv download links, download the file

        Psuedocode:
        - Try to request the data given the default URL schema, and if possible, [load it directly into a DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
        """
        df = pd.DataFrame()

        try:
            path = self.apiBaseURL + self.defaultPath + url
            df = pd.read_csv(path, encoding="ISO-8859-1")
        except Exception as e:
            print(f"[Error]: {e}")

        return df
