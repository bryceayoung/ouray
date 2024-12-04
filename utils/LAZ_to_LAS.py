import sys
import traceback
import pylas
import laspy
import os
from laspy import LazBackend

try:
    print('Running LAZ_to_LAS.py')
    
    def convert_laz_to_las(in_laz, out_las):
        las = laspy.read(in_laz, laz_backend = LazBackend.Laszip)
        las = laspy.convert(las)
        las.write(out_las)        
    
    in_dir = 'F:/_BRYCE/LiDAR/Ouray_County/laz_catalog'
    out_dir = 'F:/_BRYCE/LiDAR/Ouray_County/las_catalog'
    
    # Walk through input directory to find all laz files
    for (dirpath, dirnames, filenames) in os.walk(in_dir):
        for inFile in filenames:
            if inFile.endswith('.laz'):	
                in_laz = os.path.join(dirpath,inFile)
                
                # OPTION 1: Generate las file in the same folder
                # out_las = in_laz.replace('laz', 'las') 
                # OPTION 2: Generate las file in different folder (out_dir)
                out_las = os.path.join(out_dir, inFile.replace('.laz', '.las'))

                print('working on file: ',out_las)
                convert_laz_to_las(in_laz, out_las)
                             
    print('Finished without errors - LAZ_to_LAS.py')
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    print('Error in read_xmp.py')
    print ("PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1]))    
