# Define a function `hiz` to create home ignition zone geometries from building footprints and specified distances
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