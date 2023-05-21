import pytest
import sys
import pandas as pd
sys.path.append('../src/WeatherStation')
from ClimateDataRequester import ClimateDataRequester as cr

def getTestList():
    testList = [
        "climate_daily_AB_3010010_2004-07_P1D.csv",
        "climate_daily_AB_3010010_2004-08_P1D.csv",
        "climate_daily_AB_3010010_2020-09_P1D.csv",
        "climate_daily_AB_3010010_2020-10_P1D.csv",
        "climate_daily_AB_3010010_2021-11_P1D.csv",
        "climate_daily_AB_3010010_2021-12_P1D.csv",
        "climate_daily_AB_3010010_2022-01_P1D.csv",
        "climate_daily_AB_3010010_2022-02_P1D.csv",
    ]
    return testList

def test_trim_by_date_lowest():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2004, 2004)
    assert len(resultList) == 2

def test_trim_by_date_highest():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2022, 2022)
    assert len(resultList) == 2

def test_trim_by_date_middle():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2020, 2020)
    assert len(resultList) == 2

def test_trim_by_date_span():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2020, 2021)
    assert len(resultList) == 4

def test_trim_by_date_all():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2004, 2022)
    assert len(resultList) == 8

def test_trim_by_date_not_exist_low():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2003, 2003)
    assert len(resultList) == 0

def test_trim_by_date_not_exist_high():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2023, 2023)
    assert len(resultList) == 0

def test_trim_by_date_not_exist_middle():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2005, 2005)
    assert len(resultList) == 0

def test_trim_by_date_beyond():
    req = cr()
    testList = getTestList()
    assert len(testList) == 8
    resultList = req.trim_by_date(testList, 2004, 2023)
    assert len(resultList) == 8

def test_pull_data():
    req = cr()
    df = req.pull_data("AB/climate_daily_AB_3010010_2004-07_P1D.csv")
    assert not df.empty

if __name__ == '__main__':
    test_ClimateDataRequester()
