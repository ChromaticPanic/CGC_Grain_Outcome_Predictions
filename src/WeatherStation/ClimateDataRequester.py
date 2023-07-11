"""Climate Data Requester pulls weather station data.

requests data from the Climate Data Online web service and returns a pandas dataframe

Typical usage example:

  req = ClimateDataRequester()
  df = req.get_data(stationName: str)
"""
import lxml.html  # type: ignore
import requests as rq  # type: ignore
import pandas as pd  # type: ignore
import urllib3
import typing
import sys

# import ipyparallel as ipp


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
        df = pd.DataFrame()
        baseUrl = f"https://api.weather.gc.ca/collections/climate-hourly/items?datetime={startYear}-01-01%2000:00:00/{endYear}-12-31%2000:00:00&CLIMATE_IDENTIFIER="
        midUrl = "&sortby=PROVINCE_CODE,CLIMATE_IDENTIFIER,LOCAL_DATE&f=csv&limit=10000&startindex="
        offset = 10000

        try:
            currIndex = 0
            newData = pd.read_csv(baseUrl + stationID + midUrl + str(currIndex))
            while len(newData.index) > 0:
                df = pd.concat([df, newData])
                currIndex += offset

                newData = pd.read_csv(baseUrl + stationID + midUrl + str(currIndex))
        except Exception:
            5 + 5

        return df

    def get_data(
        self, province: str, stationID: str, startYear: int = 2022, endYear: int = 2022
    ) -> pd.DataFrame:
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
        resp = rq.get(
            self.apiBaseURL + self.defaultPath + province + "/",
            headers=self.headers,
            verify=False,
        )
        result = []
        if resp.status_code == 200:
            tree = lxml.html.fromstring(resp.text)
            for link in tree.xpath("//a/@href"):
                if link.endswith(".csv"):
                    if not stationID:
                        result.append(link)
                    elif link.find(stationID) > -1:
                        result.append(link)

        return result

    def trim_by_date(self, csvList: list, startYear: int, endYear: int) -> list:
        DATEPOS = 4
        result = []
        for i in range(len(csvList) - 1, -1, -1):
            item = csvList[i]
            entry = item.split("_")
            year = int(str(entry[DATEPOS])[:4])
            if year >= startYear and year <= endYear:
                result.append(item)
        return result

    def pull_data(self, url: str) -> pd.DataFrame:
        df = pd.DataFrame()
        try:
            path = self.apiBaseURL + self.defaultPath + url
            df = pd.read_csv(path, encoding="ISO-8859-1")
            return df
        except Exception as e:
            print("Error: " + str(e))
            return df
