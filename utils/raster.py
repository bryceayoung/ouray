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

def write_raster(output_path, raster_array, profile):
    """
    Writes a NumPy array as a raster file using Rasterio.

    Parameters:
    - output_path (str): Path to save the raster file.
    - raster_array (numpy.ndarray): 2D NumPy array of raster values.
    - profile (dict): Rasterio profile (metadata) containing transform, CRS, dtype, etc.

    Returns:
    - None (writes raster to file)
    """
    
    # Ensure the data type matches the profile
    if raster_array.dtype != np.dtype(profile["dtype"]):
        raster_array = raster_array.astype(profile["dtype"])

    # Write raster
    with rio.open(output_path, "w", **profile) as dst:
        dst.write(raster_array, 1)  # Writing as Band 1

    print(f"✅ Raster written to: {output_path}")

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

def ez_clip(raster, reference, profile):
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
    raster1_clipped, raster1_profile = ez_clip(raster1, raster2, raster1_profile)
    """

    clipped_data = raster[:reference.shape[0], :reference.shape[1]]
    
    profile.update({
        'height': reference.shape[0],
        'width': reference.shape[1]
    })
    return clipped_data, profile

import numpy as np
from affine import Affine
import rasterio as rio

def clip_raster(large_raster, small_raster, large_profile, small_profile):
    """
    Clips a larger raster to the same extent and shape as a smaller raster and applies a nodata mask.
    
    Parameters:
    - large_raster (numpy array): The larger raster to be clipped.
    - small_raster (numpy array): The smaller raster defining the clip extent.
    - large_profile (dict): Metadata (profile) of the larger raster.
    - small_profile (dict): Metadata (profile) of the smaller raster.

    Returns:
    - clipped_raster (numpy array): The clipped and masked raster.
    - updated_profile (dict): Updated profile with new 'width', 'height', and 'transform'.
    """

    # Extract transform and shape details
    large_transform = large_profile["transform"]
    small_transform = small_profile["transform"]
    small_height, small_width = small_raster.shape

    # Calculate pixel offsets (row/col) in the large raster corresponding to the small raster's extent
    row_off = int((small_transform.f - large_transform.f) / large_transform.e)
    col_off = int((small_transform.c - large_transform.c) / large_transform.a)

    # Clip the large raster to match the small raster’s extent
    clipped_raster = large_raster[row_off:row_off + small_height, col_off:col_off + small_width]

    # Apply the small raster's nodata mask
    small_nodata = small_profile.get("nodata", None)
    large_nodata = large_profile.get("nodata", None)

    if small_nodata is not None:
        mask = (small_raster == small_nodata)
        clipped_raster[mask] = large_nodata if large_nodata is not None else np.nan

    # Update the transform for the clipped raster
    updated_transform = rio.transform.from_origin(
        small_transform.c, small_transform.f,  # Top-left corner of the smaller raster
        small_transform.a, -small_transform.e  # Pixel width/height (unchanged)
    )

    # Update the profile
    updated_profile = large_profile.copy()
    updated_profile.update({
        'height': small_height,
        'width': small_width,
        'transform': updated_transform
    })

    return clipped_raster, updated_profile