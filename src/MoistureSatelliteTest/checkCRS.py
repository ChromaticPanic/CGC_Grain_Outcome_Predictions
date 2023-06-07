import xarray as xr
import geopandas as gpd

# Load the shapefile into a GeoDataFrame
gdf = gpd.read_file('lpr_000b16a_e.shp')

# Print the CRS of the shapefile
print("CRS of the shapefile:")
print(gdf.crs)
print("\n")

# Open the NetCDF file
dataset = xr.open_dataset('demo7.nc')

# Print the metadata of the NetCDF file
print("Attributes of the NetCDF file:")
print(dataset.variables)

