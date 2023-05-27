import pytest
import sys
sys.path.append('../src/docker')

from fixCSV import CSVBorderReader

def test_read_file():
    borderReader = CSVBorderReader()
    borderReader.read('provBoundaries.csv')

    assert(borderReader.input)

def test_process_data():
    borderReader = CSVBorderReader()
    borderReader.read('provBoundaries.csv')
    provinces, borders = borderReader.getGISBorders()