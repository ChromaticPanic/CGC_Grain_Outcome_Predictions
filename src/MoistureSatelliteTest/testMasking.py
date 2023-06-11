from netCDF4 import Dataset
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pyproj import CRS
import regionmask
from shapely.geometry import Polygon

shapefile_path = 'C:\jay projects\school\COMP 4560\CGC_Grain_Outcome_Predictions\src\MoistureSatelliteTest\lpr_000b16a_e.shp'
netcdf_file_path = 'C:\jay projects\school\COMP 4560\CGC_Grain_Outcome_Predictions\src\MoistureSatelliteTest\perfectDemo.nc'

shapefile = gpd.read_file(shapefile_path)
#match the netCDF CRS (EPSG:4326)
netcdf_crs = CRS.from_epsg(4326)
shapefile_reprojected = shapefile.to_crs(netcdf_crs)

dataset = xr.open_dataset(netcdf_file_path)
#print(dataset['sm'].values)
manitoba = shapefile_reprojected[shapefile_reprojected['PRNAME'] == 'Saskatchewan']
mask = regionmask.mask_geopandas(manitoba, dataset.lon, dataset.lat)
masked_data = dataset.where(mask)

output_csv_file = 'C:\jay projects\school\COMP 4560\CGC_Grain_Outcome_Predictions\src\MoistureSatelliteTest\sm_data_demo7_Saskatchewan.csv'


sm_data = masked_data['sm'].values
sm_data_2d = sm_data[0, :, :]
df = pd.DataFrame(sm_data_2d)
df.to_csv(output_csv_file, index=False)

average_sm = np.nanmean(masked_data['sm'].values)
print("Average Surface Soil Moisture:", average_sm)

print(shapefile_reprojected.crs)
print(dataset.crs)

# print(masked_data['sm'].values)
#print(masked_data['flag'].values)
print(masked_data['sm'].values)
