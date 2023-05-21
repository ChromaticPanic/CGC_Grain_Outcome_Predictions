import pytest
import sys
sys.path.append('../src/WeatherStation')
from ClimateDataRequester import ClimateDataRequester as cr

@pytest.mark.slowTests
def test_ClimateDataRequester():
    req = cr()
    result = req.get_url_list("AB")
    assert len(result) > 0   


    