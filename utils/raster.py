import rasterio as rio
import numpy as np

class FillNaN:
    def __init__(self, method="mean"):
        """
        Initialize the FillNaN object with the desired interpolation method.

        Args:
            method (str): The statistic to compute in the filter window.
                          Options are "mean", "min", "max". Default is "mean".
        """
        self.method = method

    def __call__(self, window):
        """
        Apply the chosen interpolation method to a given window.

        Args:
            window (numpy.ndarray): The array of values in the filter window.

        Returns:
            float: The result of the interpolation.
        """
        valid_values = window[~np.isnan(window)]  # Exclude NaN values
        if len(valid_values) > 0:
            if self.method == "mean":
                return np.mean(valid_values)
            elif self.method == "min":
                return np.min(valid_values)
            elif self.method == "max":
                return np.max(valid_values)
            else:
                raise ValueError(f"Unsupported method: {self.method}")
        else:
            return 0  # If all values in the window are NaN, return 0
        
    ''''
    Example usage of class FillNaN: 
    # Use mean interpolation
    fill_mean = FillNaN(method="mean")
    arr_filled_mean = generic_filter(arr, fill_mean, size=(3, 3), mode='reflect')

    # Use min interpolation
    fill_min = FillNaN(method="min")
    arr_filled_min = generic_filter(arr, fill_min, size=(3, 3), mode='reflect')

    # Use max interpolation
    fill_max = FillNaN(method="max")
    arr_filled_max = generic_filter(arr, fill_max, size=(3, 3), mode='reflect')
    '''

def read_raster(file_path, layer=None, transform=False, shape=False, profile=False, crs=False):
    """
    Reads rasters and assigns them to numpy array objects

    Parameters:
    - file_path (str): path to the raster file
    - layer (int): the layer to read (default is None which will read all layers)
    - transform (bool): returns the raster transform (default is false)
    - shape (bool): returns the raster shape (default is false)
    - profile (bool): returns the raster profile, which is all GDAL metadata (default is false)
    - crs (bool): returns the raster crs (default is false)

    Returns:
    - tuple of requested objects

    Dependencies:
    - import numpy as np
    - import rasterio as rio

    --------------------------------------
    Example usage for single-layer raster:
    raster, raster_transform, raster_crs = read_raster('file_path.tif', layer=1, transform=True, crs=True)

    Example usage for multi-layer raster:
    raster_stack, raster_stack_profile = read_raster('file_path.tif', profile=True)

    """
    with rio.open(file_path) as src:
        data = src.read(layer)
        return_values = [data]
        if transform:
            return_values.append(src.transform)
        if shape:
            return_values.append(src.shape)
        if profile:
            return_values.append(src.profile)
        if crs:
            return_values.append(src.crs)
    
    return tuple(return_values) if len(return_values) > 1 else data

import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import matplotlib.pyplot as plt

def mosaic_rasters(input_files, output_file):
    """
    Mosaics multiple rasters into a single raster.

    Args:
        input_files (list): List of file paths to the input rasters.
        output_file (str): Path to the output raster.

    Returns:
        None

    Example usage:
        input_files = [
            "path/to/raster1.tif",
            "path/to/raster2.tif"
        ]
        output_file = "path/to/mosaic.tif"

        mosaic_rasters(input_files, output_file)
    """
    # Open all rasters and add them to a list
    src_files_to_mosaic = [rasterio.open(f) for f in input_files]

    # Merge rasters
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Copy the metadata from one of the input rasters
    out_profile = src_files_to_mosaic[0].profile.copy()
    out_profile.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans
    })

    # Write the mosaic to the output file
    with rasterio.open(output_file, "w", **out_profile) as dest:
        dest.write(mosaic)

    # Close all input files
    for src in src_files_to_mosaic:
        src.close()

    print(f"Mosaic written to {output_file}")

def clip_raster_to_shape(raster, reference, profile):
    """
    Clips a raster to the extent of a reference raster and updates the metadata with new dimensions.
    Assumes rasters have the same upper left pixel coordinate (affine transform).
    Assumes 2-dimensional arrays e.g. shape = (10, 10) as opposed to (1, 10, 10)

    Parameters:
    - raster(numpy array): the numpy array to be clipped
    - reference(numpy array): the numpy array to clip to
    - profile(dict): the GDAL profile (metadata) of the raster to be clipped

    Returns:
    - clipped_data (numpy array): clipped raster with dimensions matching the reference
    - profile (dict): updates 'width' and 'height' values of existing profile
    
    Dependencies:
    - import numpy as np

    ------------------------------
    Example usage:
    raster1_clipped, raster1_profile = clip_raster_to_shape(raster1, raster2, raster1_profile)
    """

    clipped_data = raster[:reference.shape[0], :reference.shape[1]]
    
    profile.update({
        'height': reference.shape[0],
        'width': reference.shape[1]
    })
    return clipped_data, profile

from rasterio.features import rasterize

def rast_and_write(gdf, dst_path, profile, mask=None, dtype='float32', nodata=-9999, **kwargs):
    '''
    Function to rasterize a shapefile such as fire perimeters and write it to a tif file

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

    in_shapes = [perims1, perims2, perims3, perims4]
    out_rasters = ['file/path/perims1_raster.tif', 'file/path/perims2_raster.tif', 'file/path/perims3_raster.tif', 'file/path/perims4_raster.tif']
    
    for gdf, dst_path in zip(in_shapes, out_rasters):
        rast_and_write(gdf, dst_path, profile=profile, mask=state_boundary_raster)

    '''
    # Update the profile with any additional keyword arguments
    profile.update(kwargs)

    # Create the rasterized data
    rasterized = rasterize(
        [(geom, 1) for geom in in_shape.geometry],
        out_shape=(profile['height'], profile['width']),
        fill=0,
        transform=profile['transform'],
        dtype=dtype
    )

    # Apply the mask, if provided
    if mask is not None:
        rasterized = np.where(mask == 1, rasterized, nodata)

    # Write the rasterized result to the output file
    with rio.open(out_raster, 'w', **profile) as dst:
        dst.write(rasterized, 1)