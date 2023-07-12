import pandas as pd  # type: ignore
import calendar


MIN_MONTH = 1
MAX_MONTH = 12

MIN_YEAR = 1995
MAX_YEAR = 2022

NUM_WEEKS = 52


class AggregatorHelper:
    def getDatesInYr(self) -> list:
        """
        Figures out the date range for date processing - puts all 365 days as MO-DA into dates (which is returned)
        """
        dates = []  # all 365 days as MO-DA - strings

        # the month range we want to pull data from - strings
        months = [str(month) for month in range(MIN_MONTH, MAX_MONTH + 1)]
        for month in months:
            if len(month) == 1:
                month = "0" + month

            numDays = calendar.monthrange(2001, int(month))[1]
            days = [str(day) for day in range(1, numDays + 1)]

            for day in days:
                if len(day) == 1:
                    day = "0" + day

                dates.append(f"{month}-{day}")

        return dates

    def getWeeksInYr(self) -> list:
        """
        Figures out the date range for date processing - all 52 weeks are represented by an incrementing number
        """
        return [str(week) for week in range(1, NUM_WEEKS + 1)]

    def getMonthsInYr(self) -> list:
        """
        Figures out the date range for date processing - all 12 months are represented by an incrementing number
        """
        return [str(month) for month in range(MIN_MONTH, MAX_MONTH + 1)]

    def reshapeDataByDates(
        self,
        dates: list,
        agg_df: pd.DataFrame,
        data: pd.DataFrame,
        dateType: str,
    ) -> pd.DataFrame:
        """
        Reshapes data possible by all 365 dates for each year
        """
        listForDF = []  # used for faster data processing

        # the year range we want to pull data from - ints
        years = [year for year in range(MIN_YEAR, MAX_YEAR + 1)]
        uniqueDistricts = data["district"].unique()

        # get the columns we will want to pull information from
        cols = agg_df.columns.tolist()  # type: ignore
        cols.remove("district")
        cols.remove("year")

        if dateType == "dates":
            cols.remove("month")
            cols.remove("day")
        elif dateType == "weeks":
            cols.remove("week")
        elif dateType == "months":
            cols.remove("month")

        for year in years:
            print(f"Processing year: {year}")

            for district in uniqueDistricts:
                currData = {}  # for each year/district combination create a dictionary

                # adds the year and district
                currData["year"] = year
                currData["district"] = district

                # for each day we want to grab all attributes and establish them as columns i.e DATE:attribute
                for date in dates:
                    currRow = None

                    if dateType == "dates":
                        currRow = self.__getDataPerDates(year, district, date, agg_df)
                    elif dateType == "weeks":
                        currRow = self.__getDataPerWeeks(year, district, date, agg_df)
                    elif dateType == "months":
                        currRow = self.__getDataPerMonths(year, district, date, agg_df)
                    else:
                        raise ValueError(f"[ERROR] {dateType} is an invalid datetype")

                    for col in cols:  # parse each of the desired columns
                        currAttr = f"{date}:{col}"  # the current attribute which corresponds to the date and the column
                        currVal = 0  # defaults as zero incase it does not exist

                        if len(currRow[col]) == 1:
                            # the current value from the loaded data
                            currVal = currRow[col].item()

                        currData[currAttr] = currVal

                listForDF.append(currData)

        return pd.DataFrame(listForDF)

    def __getDataPerDates(self, year, district, date, agg_df):
        dateComponents = date.split("-")
        monthInt = int(dateComponents[0])
        dayInt = int(dateComponents[1])

        return agg_df.loc[
            (agg_df["year"] == year)
            & (agg_df["month"] == monthInt)
            & (agg_df["day"] == dayInt)
            & (agg_df["district"] == district)
        ]

    def __getDataPerWeeks(self, year, district, week, agg_df):
        return agg_df.loc[
            (agg_df["year"] == int(year))
            & (agg_df["week"] == int(week))
            & (agg_df["district"] == int(district))
        ]

    def __getDataPerMonths(self, year, district, month, agg_df):
        return agg_df.loc[
            (agg_df["year"] == int(year))
            & (agg_df["month"] == int(month))
            & (agg_df["district"] == int(district))
        ]
