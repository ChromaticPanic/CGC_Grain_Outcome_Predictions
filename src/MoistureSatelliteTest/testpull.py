import geopandas as gpd
import xarray as xr
import regionmask

# Load the NetCDF data
ds = xr.open_dataset('demo7.nc')

# Load the world boundaries shapefile from Natural Earth dataset
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Filter out the polygon for Manitoba
manitoba = world.query("name == 'Manitoba'")

# If no result, make sure 'Manitoba' is in the 'name' column
if manitoba.empty:
    print(world['name'].unique())

# Create a mask using regionmask
mask = regionmask.mask_geopandas(manitoba, ds.lon, ds.lat)

# Mask the 'sm' data and convert to dataframe
df = ds['sm'].where(mask).to_dataframe()

# Reset the index to make 'lat' and 'lon' normal columns
df = df.reset_index()

# Print the dataframe
print(df)

