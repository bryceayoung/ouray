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
