from netCDF4 import Dataset
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import regionmask
from shapely.geometry import Polygon

canada = gpd.read_file('lpr_000b16a_e.shp')
#canada = canada.set_crs('EPSG:4326', allow_override=True)
#canada = canada.to_crs('EPSG:3347')

manitoba = canada[canada['PRNAME'] == 'Manitoba']

dataset = xr.open_dataset('demo7.nc')

mask = regionmask.mask_geopandas(manitoba, dataset.lon, dataset.lat)

masked_data = dataset.where(mask)

print(masked_data)

