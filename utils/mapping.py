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