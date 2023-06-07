import geopandas as gpd

canada = gpd.read_file('lpr_000b16a_e.shp')

print(canada.columns)
