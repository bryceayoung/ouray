def get_hiz(footprints, z1 = 2, z2 = 10, z3 = 30, z4 = 60):
   
    '''
    Enhances a GeoDataFrame of building footprints with additional columns for home ignition zones.
    
    NOTES: 
        - The unit of measurement will depend on your CRS (assumes CRS units in meters)
        - The zones do not overlap
    
    Parameters
    ------------------
    - footprints: GeoDataFrame with building footprints.
    - z1, z2, z3, z4: Distances for the respective zones around each footprint.
    
    Returns:
    ------------------
    - GeoDataFrame with original footprints and additional columns for each zone's buffer.
    
    '''

    # Define distances
    # Subtracts the previous zones so that total distance from home is the distance specified, but zones do not overlap
    dist_z1 = z1
    dist_z2 = z2 - z1
    dist_z3 = z3 - (z1 + z2)
    dist_z4 = z4 - (z1 + z2 + z3)

    # Start with 'footprints' and buffer with '(distance = z1)'
    footprints['buffer_z1'] = footprints.buffer(distance = dist_z1)
    footprints['buffer_z2'] = footprints['buffer_z1'].buffer(distance = dist_z2)
    footprints['buffer_z3'] = footprints['buffer_z2'].buffer(distance = dist_z3)
    footprints['buffer_z4'] = footprints['buffer_z3'].buffer(distance = dist_z4)
    
    # Return enhanced GeoDataFrame
    return footprints

def simple_hiz(footprints, buffer = 2, outer = 32):
    '''
    Creates a simple ring buffer around building footprints for HIZ analysis.

    NOTES: 
        - The unit of measurement will depend on your CRS (assumes CRS units in meters)
        - Creates a single buffer ring with a gap defined by the 'buffer' and 'outer' distances.
    
    Parameters
    ------------------
    - footprints: GeoDataFrame with building footprints.
    - id_column: Name of the column in footprints containing unique identifier corresponding to geoms
    - buffer: Inner distance (from the building footprint) of the ring.
    - outer: Outer distance (from the building footprint) of the ring.

    Returns:
    ------------------
    - GeoDataFrame with original footprints with 'geometry' column as HIZ buffer.
    '''
    
    # Create buffer around footprints at the 'buffer' distance
    buffer_inner = footprints.buffer(distance = buffer)
    
    # Create outer buffer by using the 'outer' distance
    buffer_outer = footprints.buffer(distance = outer)
    
    # Calculate the difference between the two buffers to create the ring (HIZ)
    hiz = buffer_outer.difference(buffer_inner)
    
    # Create a new GeoDataFrame to hold the result
    result_gdf = footprints[['geometry']].copy()
    
    # Assign the HIZ ring as the geometry
    result_gdf['geometry'] = hiz
    
    # Return the new GeoDataFrame with HIZ geometry and matching IDs
    return result_gdf

def structures_per_zone(gdf, footprint_col, buffer_cols):
    """
    Count intersections between buffer zones and building footprints in the same GeoDataFrame.

    Parameters:
    ----------------
    - gdf: GeoDataFrame containing the footprints and buffers.
    - footprint_col: The name of the column containing footprint geometries.
    - buffer_cols: A list of column names containing buffer zone geometries.

    Returns:
    ----------------
    - A DataFrame with the counts of intersections per structure per buffer zone.
    
    Examples:
    ----------------
    buffer_cols = ['buffer_z1', 'buffer_z2', 'buffer_z3']  # Define your buffer zone columns
    counts_df = structures_per_zone(gdf, 'footprints', buffer_cols)
    counts_df.head()

    """
    # Initialize an empty DataFrame to store results
    counts_df = gdf[[footprint_col]].copy()
    for col in buffer_cols:
        counts_df[col] = 0  # Initialize counts to 0

    # Iterate over each structure in the GeoDataFrame
    for index, structure in gdf.iterrows():
        # Check intersections for each buffer zone
        for buffer_col in buffer_cols:
            # Exclude the current structure's footprint from the comparison
            other_footprints = gdf.drop(index)[footprint_col]
            # Count how many other footprints intersect with the current structure's buffer zone
            counts_df.at[index, buffer_col] = other_footprints.intersects(structure[buffer_col]).sum()

    return counts_df

import pandas as pd

def structures_in_hiz(footprints_gdf, hiz_gdf, footprint_col='geometry', hiz_col='geometry'):
    """
    Count intersections between each building footprint and its corresponding HIZ geometry.
    
    Parameters:
    ----------------
    - footprints_gdf: GeoDataFrame containing building footprints.
    - hiz_gdf: GeoDataFrame containing HIZ geometries.
    - footprint_col: The column name containing footprint geometries (default 'geometry').
    - hiz_col: The column name containing HIZ geometries (default 'geometry').

    Returns:
    ----------------
    - A DataFrame with the number of adjacent structures (intersections) for each footprint and its corresponding HIZ.
    
    Examples:
    ----------------
    result_df = structures_in_hiz(footprints_gdf, hiz_gdf)
    result_df.head()
    """
    
    # Initialize an empty list to store the counts
    intersection_counts = []

    # Iterate over each building footprint and its corresponding HIZ geometry
    for footprint_index, footprint in footprints_gdf.iterrows():
        # Get the corresponding HIZ geometry for the current footprint
        corresponding_hiz = hiz_gdf.loc[hiz_gdf.index == footprint_index, hiz_col].values[0]
        
        # Initialize the count of intersections for this footprint's HIZ zone
        count = 0
        
        # Iterate over all other footprints and check for intersections with the current footprint's HIZ zone
        for other_footprint_index, other_footprint in footprints_gdf.iterrows():
            if footprint_index != other_footprint_index:
                # Check if there's an intersection between the HIZ zone and the other footprint
                if corresponding_hiz.intersects(other_footprint[footprint_col]):
                    count += 1
        
        # Append the count and corresponding footprint index to the list
        intersection_counts.append({'footprint_index': footprint_index, 'intersections': count})

    # Convert the list of intersection counts to a DataFrame
    counts_df = pd.DataFrame(intersection_counts)
    
    # Return the resulting DataFrame
    return counts_df

from shapely.geometry import MultiPoint

def min_ssd(gdf, geom_col='geometry'):
    """
    Compute the minimum structure separation distance (SSD) between building footprints.
    
    Parameters:
    ----------------
    - gdf: GeoDataFrame containing building footprints.
    - geom_col: The column name containing footprint geometries (default 'geometry').
    
    Returns:
    ----------------
    - GeoDataFrame with an additional 'min_ssd' column representing the minimum distance to the nearest footprint.
    
    Examples:
    ----------------
    gdf = min_ssd(gdf)
    gdf.head()
    """
    
    # Initialize an empty list to store the minimum SSD values
    min_ssd_values = []

    # Iterate over each building footprint
    for index, structure in gdf.iterrows():
        # Get the outer boundary of the current footprint (geometry)
        current_boundary = structure[geom_col].boundary
        
        # Initialize a large minimum SSD value for comparison
        min_distance = float('inf')
        
        # Compare the current building footprint with all other footprints
        for other_index, other_structure in gdf.iterrows():
            if index != other_index:  # Avoid comparing the footprint to itself
                # Calculate the Euclidean distance between the current boundary and the other footprint's boundary
                distance = current_boundary.distance(other_structure[geom_col])
                
                # If this distance is smaller than the current minimum, update the min_distance
                if distance < min_distance:
                    min_distance = distance
        
        # Append the computed minimum SSD value to the list
        min_ssd_values.append(min_distance)
    
    # Add the 'min_ssd' column to the GeoDataFrame
    gdf['min_ssd'] = min_ssd_values
    
    # Return the GeoDataFrame with the 'min_ssd' column
    return gdf    

from rasterio.mask import mask
import numpy as np
import rasterio as rio
import geopandas as gpd

def raster_stats(gdf, raster_paths, rnames, stats=['mean']):
    """
    Computes summary statistics for each raster within HIZ polygons.

    Parameters:
    - gdf: GeoDataFrame with HIZ polygons
    - raster_paths: List of raster file paths
    - rnames: List of correponding raster names for column titles (same order as paths)
    - stats: List of stats to compute (options: 'mean', 'min', 'max', 'median', 'sum', 'std')

    Returns:
    - gdf with new columns for each stat per raster
    """

    # Define available stats
    stat_funcs = {
        'mean': np.nanmean,
        'min': np.nanmin,
        'max': np.nanmax,
        'median': np.nanmedian,
        'sum': np.nansum,
        'std': np.nanstd
    }

    # Check for invalid stats
    invalid_stats = [s for s in stats if s not in stat_funcs]
    if invalid_stats:
        raise ValueError(f"Invalid stats requested: {invalid_stats}")
    
    if len(raster_paths) != len(rnames):
        raise ValueError("raster_paths and rnames must have the same length.")

    # Loop through each raster
    for raster_path, rname in zip(raster_paths, rnames):
        with rio.open(raster_path) as src:
            for idx, row in gdf.iterrows():
                try:
                    # Mask raster with polygon
                    out_image, _ = mask(src, [row.geometry], crop=True, nodata=np.nan)

                    # Flatten and remove NaNs
                    data = out_image[0].flatten()
                    data = data[~np.isnan(data)]  # Keep only valid values

                    if len(data) > 0:  # Only compute if there's valid data
                        for stat in stats:
                            gdf.at[idx, f"{stat}_{rname}"] = stat_funcs[stat](data)
                    else:
                        for stat in stats:
                            gdf.at[idx, f"{stat}_{rname}"] = np.nan

                except Exception as e:
                    print(f"Error processing {raster_path} for HIZ {idx}: {e}")
                    for stat in stats:
                        gdf.at[idx, f"{stat}_{rname}"] = np.nan  # Fill with NaN if error occurs

    return gdf   