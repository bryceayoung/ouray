# This script takes a set of building footprints and creates a geomertry that encompasses all the footprints
# The purpose of this is to download only the minimum amount of LiDAR data needed for the operation

import geopandas as gpd
from shapely.geometry import Polygon

# Import polygon
gdf_g = gpd.read_file('Documents/Projects/GUC_ParcelLevelRisk/Data/Gunnison_County_Buildings/Gunnison_County_Buildings.shp') # EPSG:4326 - WGS84 - World Geodetic System 1984

#Global variables
CRS = 'EPSG:5070'    # USA Contiguous Albers Equal Area Conic Projection

# Project coordinate system
gdf_p = gdf.to_crs(CRS)

# Create a broader boundary encompassing all of the buildings
total_building_vector = gdf_p.unary_union

# Display it on a map
total_building_vector.plot()

# Save merged geometry as a shapefile
# merged_geometry.to_file("merged_geometry.shp")