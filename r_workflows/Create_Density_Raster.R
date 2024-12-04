library(lidR)

# ======================================
#  READ DATA AND VISUALIZE POINT DESNITY
# ======================================

# A. Explore the Data
# =======================
# The lidr book is available at https://r-lidar.github.io/lidRbook/io.html 
# Read thorugh that link, this script is based off chapter 2

# 1. Read a file and understand its content
# readLAS is the basic function to read in las or laz files
# Here I use a fancy R technique to read in the las file w/o having to adjust 
# all the back slashes. Using r"()" tells R that this is raw input
# Here we also use the filter argument to tell R not to read in the withheld points
# this argument, along with 'select = ' allowsus to only read in points we will
# use. Read more about these arguments in the lidr book. See all the filter arguments
# by runnig readLAS(filter = "-help")
# Replace the file path with your own.

las = readLAS(r"(G:/_BRYCE/LiDAR/Ouray_County/las_catalog/usgs_lpc_co_sanluisjuanmiguel_2020_d20_12s_yh_5045.las)", filter = "-drop_withheld")

# Let's display the basic information about our las file
las

# note the point density (9.22 points/m2) and that the unit is meters
# Let's set the cell_size based on that average point density
# Let's check and see how well half a meter looks as a raster
cell_size <-.5
density_raster <- grid_density(las, res = cell_size)

# plot the density raster 
plot(density_raster)

# Now save it out so we can pull this raster into a GIS for better visualization
# First have to load a library with writeRaster function
library(raster)
# Replace the file path with your own.
writeRaster(density_raster,r"(C:\...\density_raster.tif)")

# You might be able to see either in the R plot or in your GIS that there are 
# a lot of pixels with 0 values. Meaning our cell_size was too small for there
# to be LiDAR points in every cell. So the average points per square meter of 9.22
# was deceptive as those points are not evenly distributed with areas of high point 
# density and areas of low point density. 
# Try different cell sizes to see what is the finest resolution appropriate.