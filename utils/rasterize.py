import rasterio as rio
import numpy as np
from rasterio.transform import from_origin
from rasterio.features import rasterize

def make_prof(gdf, resolution=1, dtype='uint8', nodata=0, crs=None):
    """
    Build a rasterio profile from a GeoDataFrame and desired resolution.
    """
    # Set CRS
    if crs is None:
        print("INFO: CRS was not specified. Using CRS from GeoDataFrame by default.")
        crs = gdf.crs
    else:
        print("INFO: CRS was specified. Reprojecting GeoDataFrame to specified CRS.")
        gdf = gdf.to_crs(crs)

    # Get bounds
    minx, miny, maxx, maxy = gdf.total_bounds

    # Calculate width and height
    width = int(np.ceil((maxx - minx) / resolution))
    height = int(np.ceil((maxy - miny) / resolution))

    # Create transform (top-left origin)
    transform = from_origin(minx, maxy, resolution, resolution)

    # Build profile dictionary
    profile = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 1,
        'dtype': dtype,
        'crs': crs,
        'transform': transform,
        'nodata': nodata,
        'compress': 'lzw'
    }

    return profile


def rast_and_write(gdf, dst_path, profile, mask=None, **kwargs):
    '''
    Function to rasterize a shapefile or geopackage and write it to a tif file

    ------
    Parameters: 
    - gdf (GeoDataFrame): the shapefilfe in geodataframe format
    - dst_path (str): output file path for the raster
    - profile (dict): dictionary containing GDAL raster metadata
        - can be obtained from read_raster function, defined above
    - mask (numpy.ndarray, optional): raster mask to apply to the output to define where `nodata` should be applied
        - example would be a rasterized state boundary
    - dtype (str): data type for the raster to be created
    - nodata (float or int, optional): nodata value to assign to areas outside the mask
    - **kwargs: additional optional keyword arguments for the raster profile update

    -----
    Returns:
    None: saves the rasterized outpuit to the specified file path

    -----
    Dependencies:
    import numpy as np
    import rasterio as rio
    from rasterio.features import rasterize

    -----
    Example usage:
    raster, profile = read_raster('file/path/raster.tif', profile=True)

    in_shapes = [geom1, geom2, geom3, geom4]
    out_rasters = ['file/path/geom1_raster.tif', 'file/path/geom2_raster.tif', 'file/path/geom3_raster.tif', 'file/path/geom4_raster.tif']
    
    for gdf, dst_path in zip(in_shapes, out_rasters):
        rast_and_write(gdf, dst_path, profile=profile, mask=boundary_raster)

    '''
    # Update the profile with any additional keyword arguments
    profile.update(kwargs)

    # Create the rasterized data
    rasterized = rasterize(
        [(geom, 1) for geom in gdf.geometry],
        out_shape=(profile['height'], profile['width']),
        fill=0,
        transform=profile['transform'],
        dtype=profile['dtype']
    )

    # Apply the mask, if provided
    if mask is not None:
        rasterized = np.where(mask == 1, rasterized, nodata)

    # Write the rasterized result to the output file
    with rio.open(dst_path, 'w', **profile) as dst:
        dst.write(rasterized, 1)
    
    return rasterized