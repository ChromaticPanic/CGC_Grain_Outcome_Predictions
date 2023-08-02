# ----------------------------------------------------
# aggregatorHelper.py
#
# Assists in the aggregation proccess by reshaping columns of data by date (day, week or month)
#
# Typical usage example:
#   helper = AggregatorHelper()
#   dates = helper.getDatesInYr()
#   data = helper.reshapeDataByDates(dates, aggDF, df, "dates")
# ----------------------------------------------------
import pandas as pd
import calendar


MIN_MONTH = 1  # The month to start aggregating on
MAX_MONTH = 12  # The month to finish aggregating on

MIN_YEAR = 1995  # The year to start aggregating on
MAX_YEAR = 2022  # The year to finish aggregating on

NUM_WEEKS = 52  # The number of weeks in a year


class AggregatorHelper:
    def getDatesInYr(self) -> list:
        """
        Purpose:
        Figures out the date range for date processing - puts all 365 days as MO-DA into dates (which is returned)

        Pseudocode:
        - Get a list of the months in the month range (given as a string)
        - For each month, if there is only one character/digit, add a zero infront (i.e 01)
        - For each month, calculate the number of days (arbitrary year of 2001 is used which is not a leap year)
        - For each day, if there is only one character/digit, add a zero infront (i.e 01)
        - Finally add each month-date combination into the list we will eventually return as MO-DA
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
        Purpose:
        Figures out the date range for date processing - all 52 weeks are represented by an incrementing number

        Remarks: all 52 weeks as W - strings
        """
        return [str(week) for week in range(1, NUM_WEEKS + 1)]

    def getMonthsInYr(self) -> list:
        """
        Purpose:
        Figures out the date range for date processing - all 12 months are represented by an incrementing number

        Remarks: all 12 months as M - strings
        """
        return [str(month) for month in range(MIN_MONTH, MAX_MONTH + 1)]

    def reshapeDataByDates(
        self,
        dates: list,
        agg_df: pd.DataFrame,
        data: pd.DataFrame,
        dateType: str,
        byHarvest: bool = False,
    ) -> pd.DataFrame:
        """
        Purpose:
        Reshapes columns of data by date (day, week or month) by the full year or harvest (as indicated by the byHarvest flag)

        Pseudocode:
        - Calculate the yera range
        - Gather all the unique districts
        - Collect the aggregated column names in a list
        - Remove the irrelevant columns (these are the columns we wont want to appear once our data has been reshaped)
        - Collect the row of data that is relevant to the current date, district combination
        - Grab all attributes and establish them as key in a dictionary i.e {"DATE:attribute": value}
        - Once finished for the current date, district combination, store the dictionary into a list

        Remark: for this function to work correctly the following columns must be present given their dateType
        - dateType=dates: year, district and month, day
        - dateType=weeks: year, district and week
        - dateType=months: year, district and month

        Also note that we use a list of dictionaries since it is much faster to do so as opposed to the number of DataFrame manipulations we'd require otherwise
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
                        currRow = self.__getDataPerDates(
                            year, district, date, agg_df, byHarvest
                        )
                    elif dateType == "weeks":
                        currRow = self.__getDataPerWeeks(
                            year, district, date, agg_df, byHarvest
                        )
                    elif dateType == "months":
                        currRow = self.__getDataPerMonths(
                            year, district, date, agg_df, byHarvest
                        )
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

    def __getDataPerDates(self, year, district, date, agg_df, byHarvest):
        """
        Purpose:
        Get the data for a given date

        Psuedocode:
        - Get the different date components (format is MO-DA)
        - Convert them to integers
        - If the date is from the fall, change it to the fall/winter of the previous year so that it applies to the current harvest
        """
        dateComponents = date.split("-")
        monthInt = int(dateComponents[0])
        dayInt = int(dateComponents[1])

        if byHarvest and monthInt >= 9:
            return agg_df.loc[
                (agg_df["year"] == year - 1)
                & (agg_df["month"] == monthInt)
                & (agg_df["day"] == dayInt)
                & (agg_df["district"] == district)
            ]
        else:
            return agg_df.loc[
                (agg_df["year"] == year)
                & (agg_df["month"] == monthInt)
                & (agg_df["day"] == dayInt)
                & (agg_df["district"] == district)
            ]

    def __getDataPerWeeks(self, year, district, week, agg_df, byHarvest):
        """
        Purpose:
        Get the data for a given date

        Psuedocode:
        - Get the different date components (format is W)
        - Convert them to integers
        - If the date is from the fall/winter, change it to the fall/winter of the previous year so that it applies to the current harvest
        """
        if byHarvest and int(week) >= 33:
            return agg_df.loc[
                (agg_df["year"] == int(year) - 1)
                & (agg_df["week"] == int(week))
                & (agg_df["district"] == int(district))
            ]
        else:
            return agg_df.loc[
                (agg_df["year"] == int(year))
                & (agg_df["week"] == int(week))
                & (agg_df["district"] == int(district))
            ]

    def __getDataPerMonths(self, year, district, month, agg_df, byHarvest):
        """
        Purpose:
        Get the data for a given date

        Psuedocode:
        - Get the different date components (format is M)
        - Convert them to integers
        - If the date is from the fall/winter, change it to the fall/winter of the previous year so that it applies to the current harvest
        """
        if byHarvest and int(month) >= 9:
            return agg_df.loc[
                (agg_df["year"] == int(year) - 1)
                & (agg_df["month"] == int(month))
                & (agg_df["district"] == int(district))
            ]
        else:
            return agg_df.loc[
                (agg_df["year"] == int(year))
                & (agg_df["month"] == int(month))
                & (agg_df["district"] == int(district))
            ]
