import pytest
import sys
import numpy as np
import pandas as pd

sys.path.append("../src/WeatherStation")

from DataProcessor import DataProcessor

processor = DataProcessor()


def test_remove_inactive_stations():
    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2"]
    states = [
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
        {
            "station_id": "1",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
    ]

    processor.removeInactive(stations, states)
    assert len(stations) == 2
    assert "1" in stations.values
    assert "2" in stations.values

    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2"]
    states = [
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
        {
            "station_id": "1",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
    ]

    stations = processor.removeInactive(stations, states)
    assert len(stations) == 0
    assert "1" not in stations.values
    assert "2" not in stations.values

    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = [
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
        {
            "station_id": "1",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
        {
            "station_id": "3",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
    ]

    stations = processor.removeInactive(stations, states)
    assert len(stations) == 1
    assert "2" not in stations.values
    assert "1" in stations.values
    assert "3" not in stations.values


def test_remove_inactive_stations_all_new_stations():
    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = []

    stations = processor.removeInactive(stations, states)
    assert len(stations) == 3
    assert "1" in stations.values
    assert "2" in stations.values
    assert "3" in stations.values


def test_add_last_updated_all_values():
    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = [
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
        {
            "station_id": "1",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
        {
            "station_id": "3",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
    ]

    stations = processor.addLastUpdated(stations, states)

    assert len(stations) == 3
    assert stations["last_updated"][0] == np.datetime64("2010-05-05")
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")

    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = [
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
        {
            "station_id": "1",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
        {
            "station_id": "3",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
    ]

    stations = processor.addLastUpdated(stations, states)

    assert len(stations) == 3
    assert stations["last_updated"][0] == np.datetime64("2010-05-05")
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")
    assert stations["last_updated"][2] == np.datetime64("2010-05-05")


def test_add_last_updated_with_missing():
    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = [
        {"station_id": "1", "last_updated": np.datetime64(None), "is_active": False},
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
        {
            "station_id": "3",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
    ]

    stations = processor.addLastUpdated(stations, states)

    assert len(stations) == 3
    assert np.isnat(stations["last_updated"][0])
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")

    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = [
        {"station_id": "1", "last_updated": np.datetime64("NaT"), "is_active": False},
        {
            "station_id": "2",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": True,
        },
        {
            "station_id": "3",
            "last_updated": np.datetime64("2010-05-05"),
            "is_active": False,
        },
    ]

    stations = processor.addLastUpdated(stations, states)

    assert len(stations) == 3
    assert np.isnat(stations["last_updated"][0])
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")
    assert stations["last_updated"][1] == np.datetime64("2010-05-05")

    stations = pd.DataFrame()
    stations["station_id"] = ["1", "2", "3"]
    states = [
        {"station_id": "1", "last_updated": np.datetime64(None), "is_active": False},
        {"station_id": "2", "last_updated": np.datetime64(None), "is_active": True},
        {"station_id": "3", "last_updated": np.datetime64("NaT"), "is_active": False},
    ]

    stations = processor.addLastUpdated(stations, states)

    assert len(stations) == 3
    assert np.isnat(stations["last_updated"][0])
    assert np.isnat(stations["last_updated"][0])
    assert np.isnat(stations["last_updated"][0])


def test_find_latest_date():
    listOfDates = [
        np.datetime64("2010-05-05"),
        np.datetime64("2000-02-01"),
        np.datetime64("2012-12-05"),
    ]
    latestDate = pd.to_datetime(processor.findLatestDate(listOfDates))

    assert latestDate.year == 2012
    assert latestDate.month == 12
    assert latestDate.day == 5


def test_empty_find_latest_date():
    listOfDates = []
    latestDate = processor.findLatestDate(listOfDates)
    assert not latestDate


def test_find_latest_date_with_invalid_entries():
    listOfDates = [
        np.datetime64("2010-05-05"),
        np.datetime64("NaT"),
        np.datetime64("2000-02-01"),
        np.datetime64("2012-12-05"),
        np.datetime64("NaT"),
    ]
    latestDate = pd.to_datetime(processor.findLatestDate(listOfDates))

    assert latestDate.year == 2012
    assert latestDate.month == 12
    assert latestDate.day == 5

    listOfDates = [
        np.datetime64("2010-05-05"),
        np.datetime64(None),
        np.datetime64("2000-02-01"),
        np.datetime64("2012-12-05"),
        np.datetime64(None),
    ]
    latestDate = pd.to_datetime(processor.findLatestDate(listOfDates))

    assert latestDate.year == 2012
    assert latestDate.month == 12
    assert latestDate.day == 5


def test_find_latest_date_all_invalid():
    listOfDates = [np.datetime64(None), np.datetime64(None), np.datetime64("NaT")]
    latestDate = pd.to_datetime(processor.findLatestDate(listOfDates))

    assert not latestDate


def test_calc_date_range():
    firstYearWithData = 2000
    lastUpdated = np.datetime64("2001-01-01")

    lastYearWithData = 2002
    currentYear = 2003

    minYear, maxYear = processor.calcDateRange(
        firstYearWithData, lastUpdated, lastYearWithData, currentYear
    )

    assert minYear == 2001
    assert maxYear == 2002

    firstYearWithData = 2001
    lastUpdated = np.datetime64("2000-01-01")

    lastYearWithData = 2003
    currentYear = 2002

    minYear, maxYear = processor.calcDateRange(
        firstYearWithData, lastUpdated, lastYearWithData, currentYear
    )

    assert minYear == 2001
    assert maxYear == 2002

    firstYearWithData = 2050
    lastUpdated = np.datetime64("2000-01-01")

    lastYearWithData = 2003
    currentYear = 2050

    minYear, maxYear = processor.calcDateRange(
        firstYearWithData, lastUpdated, lastYearWithData, currentYear
    )

    assert minYear == 2050
    assert maxYear == 2003


def test_calc_date_range_all_equal():
    firstYearWithData = 5
    lastUpdated = np.datetime64("0005-01-01")
    lastYearWithData = 5
    currentYear = 5

    minYear, maxYear = processor.calcDateRange(
        firstYearWithData, lastUpdated, lastYearWithData, currentYear
    )

    assert minYear == 5
    assert maxYear == 5


def test_calc_date_range_last_updated_null():
    firstYearWithData = 5
    lastUpdated = np.datetime64(None)
    lastYearWithData = 5
    currentYear = 5

    minYear, maxYear = processor.calcDateRange(
        firstYearWithData, lastUpdated, lastYearWithData, currentYear
    )

    assert minYear == 5
    assert maxYear == 5


def test_calc_date_range_throws_error():
    firstYearWithData = None
    lastUpdated = np.datetime64("2000-05-05")
    lastYearWithData = 5
    currentYear = 5

    try:
        minYear, maxYear = processor.calcDateRange(
            firstYearWithData, lastUpdated, lastYearWithData, currentYear
        )
        assert False
    except Exception:
        assert True

    firstYearWithData = 5
    lastUpdated = np.datetime64("2000-05-05")
    lastYearWithData = None
    currentYear = 5

    try:
        minYear, maxYear = processor.calcDateRange(
            firstYearWithData, lastUpdated, lastYearWithData, currentYear
        )
        assert False
    except Exception:
        assert True

    firstYearWithData = 5
    lastUpdated = np.datetime64("2000-05-05")
    lastYearWithData = 5
    currentYear = None

    try:
        minYear, maxYear = processor.calcDateRange(
            firstYearWithData, lastUpdated, lastYearWithData, currentYear
        )
        assert False
    except Exception:
        assert True

    firstYearWithData = None
    lastUpdated = np.datetime64(None)
    lastYearWithData = None
    currentYear = None

    try:
        minYear, maxYear = processor.calcDateRange(
            firstYearWithData, lastUpdated, lastYearWithData, currentYear
        )
        assert False
    except Exception:
        assert True


def test_remove_older_than():
    df = pd.DataFrame()
    df["date"] = [
        np.datetime64("2012-05-06"),
        np.datetime64("2012-05-05"),
        np.datetime64("2000-05-05"),
        np.datetime64("2012-05-07"),
    ]
    last_updated = np.datetime64("2005-05-06")
    processor.removeOlderThan(df, last_updated)

    assert len(df) == 3
    assert np.datetime64("2012-05-06") in df.values
    assert np.datetime64("2012-05-05") in df.values
    assert np.datetime64("2012-05-07") in df.values
    assert np.datetime64("2000-05-05") not in df.values


def test_remove_older_than_removes_everything():
    df = pd.DataFrame()
    df["date"] = [
        np.datetime64("2012-05-06"),
        np.datetime64("2012-05-05"),
        np.datetime64("2000-05-05"),
        np.datetime64("2012-05-07"),
    ]
    last_updated = np.datetime64("2025-05-06")
    processor.removeOlderThan(df, last_updated)

    assert len(df) == 0
    assert np.datetime64("2012-05-06") not in df.values
    assert np.datetime64("2012-05-05") not in df.values
    assert np.datetime64("2012-05-07") not in df.values
    assert np.datetime64("2000-05-05") not in df.values


def test_remove_older_than_fails():
    df = None
    last_updated = np.datetime64("2025-05-06")

    try:
        processor.removeOlderThan(df, last_updated)
        assert False
    except Exception:
        assert True

    df = pd.DataFrame()
    last_updated = np.datetime64("2025-05-06")

    try:
        removeOlderThan(df, last_updated)
        assert False
    except Exception:
        assert True

    df = pd.DataFrame()
    df["future_date"] = np.datetime64("2222-05-06")
    df["anything_other_than_date"] = np.datetime64("2225-05-06")
    last_updated = np.datetime64("2025-05-06")

    try:
        processor.removeOlderThan(df, last_updated)
        assert False
    except Exception:
        assert True


def test_remove_older_than_null_date():
    df = pd.DataFrame()
    df["date"] = [
        np.datetime64("2012-05-06"),
        np.datetime64("2012-05-05"),
        np.datetime64("2000-05-05"),
        np.datetime64("2012-05-07"),
    ]
    last_updated = np.datetime64(None)
    processor.removeOlderThan(df, last_updated)

    assert len(df) == 4
    assert np.datetime64("2012-05-06") in df.values
    assert np.datetime64("2012-05-05") in df.values
    assert np.datetime64("2012-05-07") in df.values
    assert np.datetime64("2000-05-05") in df.values

    df = pd.DataFrame()
    df["date"] = [
        np.datetime64("2012-05-06"),
        np.datetime64("2012-05-05"),
        np.datetime64("2000-05-05"),
        np.datetime64("2012-05-07"),
    ]
    last_updated = np.datetime64("NaT")
    processor.removeOlderThan(df, last_updated)

    assert len(df) == 4
    assert np.datetime64("2012-05-06") in df.values
    assert np.datetime64("2012-05-05") in df.values
    assert np.datetime64("2012-05-07") in df.values
    assert np.datetime64("2000-05-05") in df.values
