# ----------------------------------------------------
# aggregatorHelper.pyi
#
# Assists in the aggregation proccess by reshaping columns of data by date (day, week or month)
#
# Typical usage example:
#   helper = AggregatorHelper()
#   dates = helper.getDatesInYr()
#   data = helper.reshapeDataByDates(dates, aggDF, df, "dates")
# ----------------------------------------------------
import pandas as pd

class AggregatorHelper:
    def getDatesInYr(self) -> list: ...
    # ----------------------------------------------------
    # Purpose:
    # Figures out the date range for date processing - puts all 365 days as MO-DA into dates (which is returned)
    #
    # Pseudocode:
    # - Get a list of the months in the month range (given as a string)
    # - For each month, if there is only one character/digit, add a zero infront (i.e 01)
    # - For each month, calculate the number of days (arbitrary year of 2001 is used which is not a leap year)
    # - For each day, if there is only one character/digit, add a zero infront (i.e 01)
    # - Finally add each month-date combination into the list we will eventually return as MO-DA
    # ----------------------------------------------------

    def getWeeksInYr(self) -> list: ...
    # ----------------------------------------------------
    # Purpose:
    # Figures out the date range for date processing - all 52 weeks are represented by an incrementing number
    #
    # Remarks: all 52 weeks as W - strings
    # ----------------------------------------------------

    def getMonthsInYr(self) -> list: ...
    # ----------------------------------------------------
    # Purpose:
    # Figures out the date range for date processing - all 12 months are represented by an incrementing number
    #
    # Remarks: all 12 months as M - strings
    # ----------------------------------------------------

    def reshapeDataByDates(
        self,
        dates: list,
        agg_df: pd.DataFrame,
        data: pd.DataFrame,
        dateType: str,
    ) -> pd.DataFrame: ...
    # ----------------------------------------------------
    # Purpose:
    # Reshapes columns of data by date (day, week or month)
    #
    # Pseudocode:
    # - Calculate the yera range
    # - Gather all the unique districts
    # - Collect the aggregated column names in a list
    # - Remove the irrelevant columns (these are the columns we wont want to appear once our data has been reshaped)
    # - Collect the row of data that is relevant to the current date, district combination
    # - Grab all attributes and establish them as key in a dictionary i.e {"DATE:attribute": value}
    # - Once finished for the current date, district combination, store the dictionary into a list
    #
    # Remark: for this function to work correctly the following columns must be present given their dateType
    # - dateType=dates: year, district and month, day
    # - dateType=weeks: year, district and week
    # - dateType=months: year, district and month
    #
    # Also note that we use a list of dictionaries since it is much faster to do so as opposed to the number of DataFrame manipulations we'd require otherwise
    # ----------------------------------------------------
