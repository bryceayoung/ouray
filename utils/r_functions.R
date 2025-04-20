# Custom Functions Passed to .pixel_metrics() in lidR package

library(terra)
library(sf)
library(sp)
library(raster)
library(lidR)

# Canopy closure less than 2m tall
cc2m    <- function(z, RetNum) {
  return(length(z[z>0 & z<=2 & RetNum==1]) / length(z[RetNum==1]))
}
# Canopy closure 2-4m tall
cc2_4m  <- function(z, RetNum) {
  return(length(z[z>2 & z<=4 & RetNum==1]) / length(z[RetNum==1]))
}
# canopy closure 4-8m tall
cc4_8m  <- function(z, RetNum) {
  return(length(z[z>4 & z<=8 & RetNum==1]) / length(z[RetNum==1]))
}
# canopy closure 8m+ tall (max 40m)
cc8_40m <- function(z, RetNum) {
  return(length(z[z>8 & RetNum==1]) / length(z[RetNum==1]))
}