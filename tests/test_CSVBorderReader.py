import pytest, sys, os.path
sys.path.append('../src/ImportGeo')

from CSVBorderReader import CSVBorderReader

def test_default_variables():
    borderReader = CSVBorderReader()
    assert(borderReader.pathToData == './data/')
    assert(len(borderReader.input) == 0)
    assert(not borderReader.input)

def test_set_path_variable():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    assert(borderReader.pathToData == '../src/ImportGeo/Data/')

def test_read_nonexistant_file():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borderReader.read('DNE.csv')

    assert(not borderReader.input)

def test_read_None():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borderReader.read(None)

    assert(not borderReader.input)

def test_read_file():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borderReader.read('provBoundaries.csv')

    assert(borderReader.input)

def test_read_file_then_None():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borderReader.read('provBoundaries.csv')

    assert(borderReader.input)

    borderReader.read(None)

    assert(not borderReader.input)

def test_validateProvinces():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    provinces = None
    
    assert(not borderReader.hasValidProvinces(provinces))

    provinces = []
    
    assert(not borderReader.hasValidProvinces(provinces))

    provinces = []

def test_validateBorders():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borders = None
    
    assert(not borderReader.hasValidBorders(borders))

    borders = []
    
    assert(not borderReader.hasValidBorders(borders))

def test_getGISBorders_without_CSVOutput():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borderReader.read('provBoundaries.csv')
    output = borderReader.getGISBorders()

    provinces = [data[0] for data in output]
    borders = [data[1] for data in output]
    
    assert(borderReader.hasValidProvinces(provinces))
    assert(borderReader.hasValidBorders(borders))
    assert(not os.path.isfile('boundaries.csv'))

def test_getGISBorders_with_CSVOutput():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')
    borderReader.read('provBoundaries.csv')
    output = borderReader.getGISBorders(True)

    provinces = [data[0] for data in output]
    borders = [data[1] for data in output]
    
    assert(borderReader.hasValidProvinces(provinces))
    assert(borderReader.hasValidBorders(borders))

    assert(os.path.isfile('boundaries.csv'))

    os.remove('boundaries.csv')

    assert(not os.path.isfile('boundaries.csv'))

def test_getGISBorders_without_input():
    borderReader = CSVBorderReader('../src/ImportGeo/Data/')

    output = borderReader.getGISBorders()

    assert(not output)
    assert(not os.path.isfile('boundaries.csv'))

    output = borderReader.getGISBorders(True)

    assert(not output)
    assert(not os.path.isfile('boundaries.csv'))