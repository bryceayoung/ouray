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