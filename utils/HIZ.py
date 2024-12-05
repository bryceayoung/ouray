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

def map_hiz(buildings_gdf, buffers_dict, center_coord, zoom = 10): # Optional: county_gdf
    """
    Create a Folium map with building footprints and buffer zones.

    Parameters:
    -----------------
    - buildings_gdf: GeoDataFrame or GeoSeries for the building footprints.
    - buffers_dict: Dictionary of GeoDataFrames or GeoSeries for buffer zones, keyed by buffer names.
    - center_coord: The central point for the map, as [latitude, longitude].
    - zoom: Initial zoom level for the map. (default = 10)
    
    Returns:
    -----------------
    Map
    
    Example Usage:
    -----------------
    
    BUILDINGS = gdf['footprints']
    BUFFERS = {
        'Z1': gdf['buffer_z1'],
        'Z2': gdf['buffer_z2'],
        'Z3': gdf['buffer_z3'],
        # Add more buffers as needed
    }
    CENTER_COORD = [50.000000, -100.000000]
    ZOOM = 10
    
    m = map_hiz(BUILDINGS, BUFFERS, CENTER_COORD, ZOOM)
    
    m
    
    """
    # Initialize map
    m = folium.Map(location=center_coord, zoom_start=zoom)

    # Add building footprints
    folium.GeoJson(
        buildings_gdf,
        style_function=lambda feature: {
            'color': 'steelblue',
            'weight': 2,
            'fillColor': 'steelblue',
            'fillOpacity': 0.5,
        },
        name='Buildings',
    ).add_to(m)

    # Add buffer zones
    buffer_styles = {
        'Z1': {'color': 'red', 'fillColor': 'red', 'fillOpacity': 0.3},
        'Z2': {'color': 'orange', 'fillColor': 'orange', 'fillOpacity': 0.3},
        'Z3': {'color': 'yellow', 'fillColor': 'yellow', 'fillOpacity': 0.3},
        # Add more styles if necessary
    }

    for buffer_name, buffer_gdf in buffers_dict.items():
        style = buffer_styles.get(buffer_name, {'color': 'gray', 'fillColor': 'gray', 'fillOpacity': 0.3})  # Default style
        folium.GeoJson(
            buffer_gdf,
            style_function=lambda feature, style=style: {
                'color': style['color'],
                'weight': 1,
                'fillColor': style['fillColor'],
                'fillOpacity': style['fillOpacity'],
            },
            name=buffer_name,
        ).add_to(m)

    # # Optional: Add county boundary
    # folium.GeoJson(
    #     county_gdf,
    #     style_function=lambda feature: {
    #         'color': 'steelblue',
    #         'weight': 1,
    #         'fillColor': None,
    #         'fillOpacity': 0.05,
    #     },
    #     name='County Boundary',
    # ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    return m

def structures_per_zone(gdf, footprint_col, buffer_cols):
    """
    Count intersections between a given footprint and buffer zones in the same GeoDataFrame.

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