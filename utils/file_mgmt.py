import os
import re

'''
This class finds and identifies the names of missing tiles from a LAS catalog.
It works well with tiles that have a ordinal, numerical naming convention, because it finds numbers where just 1 number was skipped.

Parameters:
-----------------------
las_directory(str): folder path containing las files to be searched
file_prefix(str): prefix of all files to be searched
file_suffix(str): suffix of all files to be searched
pattern(str): file pattern that the parser is looking for

Returns:
------------------------
get_tile_numbers: returns list of tile numbers
find_missing_tiles: returns list of file names of the missing files

Example usage
------------------
parser = LASCatalogParser(
    las_directory=r'F:/_BRYCE/LiDAR/Ouray_County/las_catalog',
    file_prefix="usgs_lpc_co_sanluisjuanmiguel_2020_d20_13s_bc_",
    file_suffix=".las",
    pattern=r'usgs_lpc_co_sanluisjuanmiguel_2020_d20_13s_bc_(\d+)\.las'
)

missing_tiles = parser.find_missing_tiles()
print("Missing file names:", len(missing_tiles))
print(missing_tiles)
'''

class LASCatalogParser:
    def __init__(self, las_directory, file_prefix, file_suffix, pattern):
        self.las_directory = las_directory
        self.file_prefix = file_prefix
        self.file_suffix = file_suffix
        self.pattern = pattern

    def get_tile_numbers(self):
        tile_numbers = []
        for filename in os.listdir(self.las_directory):
            match = re.match(self.pattern, filename)
            if match:
                tile_numbers.append(int(match.group(1)))
        return sorted(tile_numbers)

    def find_missing_tiles(self):
        tile_numbers = self.get_tile_numbers()
        missing_files = []
        for i in range(len(tile_numbers) - 1):
            gap = tile_numbers[i+1] - tile_numbers[i]
            for missing_tile in range(1, gap):
                missing_files.append(f"{self.file_prefix}{tile_numbers[i] + missing_tile}{self.file_suffix}")
        return missing_files


import os
import shutil

def copy_unique_files(src_dir, dst_dir, file_prefix, file_suffix, folder_range):
    """
    Copies LAZ or LAS files from subfolders into a destination folder, avoiding duplicates.

    Args:
        src_dir (str): Source directory containing subfolders.
        dst_dir (str): Destination directory to copy files into.
        file_prefix (str): Prefix to match files.
        file_suffix (str): Suffix to match files.
        folder_range (range): Range of subfolder numbers (e.g., range(1, 24)).

    Returns:
        None

    # Example usage
copy_unique_files(
    src_dir="F:/_BRYCE/LiDAR/Ouray_County",
    dst_dir="F:/_BRYCE/LiDAR/Ouray_County/laz_catalog",
    file_prefix="usgs_lpc_co_sanluisjuanmiguel_2020_",
    file_suffix=".laz",
    folder_range=range(1, 24)
)
    """
    # Make sure the destination folder exists
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # Set to track filenames and avoid duplicates
    copied_files = set()

    # Loop through all fishnet folders
    for folder_num in folder_range:
        fishnet_folder = os.path.join(src_dir, f"fishnet_{folder_num}")
        
        # Check if the fishnet folder exists
        if os.path.exists(fishnet_folder):
            for file_name in os.listdir(fishnet_folder):
                # Check if the file matches the criteria
                if file_name.startswith(file_prefix) and file_name.endswith(file_suffix):
                    file_path = os.path.join(fishnet_folder, file_name)
                    if file_name not in copied_files:
                        shutil.copy2(file_path, dst_dir)
                        copied_files.add(file_name)
                        print(f"Copied: {file_name}")
                    else:
                        print(f"Duplicate skipped: {file_name}")
        else:
            print(f"Folder not found: {fishnet_folder}")

    print("Done and dusted. Go check out your files and then take 10.")
