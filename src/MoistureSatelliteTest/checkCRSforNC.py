import netCDF4 as nc
import pyproj

# Open the netCDF file
netcdf_file = nc.Dataset('/home/student/bhandar1/CGC_Grain_Outcome_Predictions/src/MoistureSatelliteTest/demo7.nc')

# List of possible CRS definitions
crs_definitions = [
    # Example CRS definitions, add more as needed
    {'name': 'WGS84', 'proj': 'latlong', 'datum': 'WGS84'},
    {'name': 'EPSG:4326', 'proj': 'latlong', 'datum': 'WGS84'},
    {'name': 'EPSG:3857', 'proj': 'merc', 'datum': 'WGS84'}
]

# Loop through variables
for var_name, var in netcdf_file.variables.items():
    # Check if the variable is a coordinate variable
    if var_name in netcdf_file.dimensions:
        # Extract the variable values
        var_values = var[:]

        # Perform checks based on the values
        # Example checks, modify or add more as needed
        if all(-180 <= value <= 180 for value in var_values):
            # CRS is likely WGS84 longitude-latitude
            crs_definition = crs_definitions[0]
            break
        elif all(-90 <= value <= 90 for value in var_values):
            # CRS is likely WGS84 latitude-longitude
            crs_definition = crs_definitions[1]
            break

# Interpret the CRS based on the selected definition
if 'crs_definition' in locals():
    crs = pyproj.Proj(proj=crs_definition['proj'], datum=crs_definition['datum'])
    print("CRS Name:", crs_definition['name'])
    print("CRS Projection:", crs.srs)
else:
    print("CRS information not found in the netCDF file.")

# Close the netCDF file
netcdf_file.close()
