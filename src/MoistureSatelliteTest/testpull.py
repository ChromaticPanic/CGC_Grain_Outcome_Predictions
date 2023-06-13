import pandas as pd
import xarray as xr
import geopandas as gpd
import numpy as np
from pyproj import CRS
from shapely import Point
import os

# getting path
folder_path = r"C:\jay projects\school\COMP 4560\images\2004"
shapefile_path = r"C:\jay projects\school\COMP 4560\CGC_Grain_Outcome_Predictions\src\MoistureSatelliteTest\lpr_000b16a_e.shp"

# preprocess shape file
shapefile = gpd.read_file(shapefile_path)
netcdf_crs = CRS.from_epsg(4326)
# Reproject the shapefile to match the netCDF CRS
shapefile = shapefile.to_crs(netcdf_crs)

mb_geometry = shapefile[shapefile['PRENAME'] == "Manitoba"].geometry[6]
sk_geometry = shapefile[shapefile['PRENAME'] == "Saskatchewan"].geometry[7]
ab_geometry = shapefile[shapefile['PRENAME'] == "Alberta"].geometry[8]

study_region_geometry = [mb_geometry, sk_geometry, ab_geometry]
study_region_name = ["Manitoba", "Saskatchewan", "Alberta"]


# netcdf file processing

# Get a list of all files in the folder
file_list = os.listdir(folder_path)

# Filter the file list to include only NetCDF files
nc_file_list = [filename for filename in file_list if filename.endswith('.nc')]

points_in_region = []

print("Total number of files : ", len(nc_file_list))

count  = 1

for nc_file in nc_file_list:
    # Construct the full file path
    file_path = os.path.join(folder_path, nc_file)
    # print(file_path)
    dataset = xr.open_dataset(file_path)

    print("Working on file number : ",count)

    # seperating lon and lat
    latitude = dataset.lat.values
    longitude = dataset.lon.values

    sm_data = dataset['sm'].values

    dateTime = dataset['time'].values[0]
    date = np.datetime_as_string(dateTime, unit='D')

    dataset.close()

    for region_name, region_geometry in zip(study_region_name, study_region_geometry):

        print("I am working on ", region_name)

        for i in range(len(latitude)):
            lat = latitude[i]
            for j in range(len(longitude)):
                lon = longitude[j]

                # Create a Point object for each coordinate
                point = Point(lon, lat)

                if region_geometry.contains(point):
                    sm = sm_data[0, i, j]

                    # Store the information in a dictionary or perform desired actions
                    point_info = {
                        "date": date,
                        "province": region_name,
                        "latitude": lat,
                        "longitude": lon,
                        "soil_moisture": sm
                    }
                    points_in_region.append(point_info)
    count += 1

print("I am out XDXDXD")
df = pd.DataFrame(points_in_region)

print(df)




