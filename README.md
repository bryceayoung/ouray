# Ouray Parcel Risk
**Author**: Bryce A Young, 2023-2025  
**Correspondence**: bryce.young@umontana.edu  
**Institution**: University of Montana, National Center for Landscape Fire Analysis  

## Overview
In this repository, I develop workflows to predict and classify parcel-level wildfire risk to homes based on the attributes of structures and their defensible space. The analysis area is Ouray County, Colorado.

## Data
There are four (4) primary data types used in this project: LiDAR, tax assessor data, and the SILVIS Global WUI raster.  
1. **LiDAR**  
LAZ files were downloaded at the [Colorado Hazard Mapping website](https://coloradohazardmapping.com/lidarDownload "LiDAR Download"). These files were produced by Quantum Spatial in June of 2020 via Airborne Laser Scanning (ALS). The point density is great enough to create 1-meter rasters from the files. The rasters that I produced with them represent certain forest canopy metrics, which I will elaborate on later.  
2. **Tax Assessor Data**  
Property records were obtained my calling the Ouray County Tax Assessor office, who were kind enough to compile and send me CSV files of property tax assessments. This tabular data contains information about each property such as year built, roof material, siding material, outbuildings, and more information that influences the vulnerability of structures to wildfire.  
3. **SILVIS Global WUI**  
The 2020 global WUI raster was obtained from [SILVIS Lab](https://zenodo.org/records/7941460 "Global Wildland Urban Interface"). It is a land class raster containing 8 different land classes which describe different types of WUI or non-WUI based on structure density, housing arrangement, and dominant surrounding vegetation. The resolution is 10m and the downloaded North America zip file contains 100km x 100km tiles.    
4. **West Region Wildfire Council Rapid Wildfire Risk Assessment scores**  
West Region Wildfire Council was kind enough to help with this project by providing me with risk assessment scores for the entire 6-county area that they cover in western Colorado, including Ouray County. These are tabular data containing the property identifier that can be spatially joined to county parcels. More information on the Rapid Wildfire Risk Assessment methodlogy can be obtained from [Meldrum et al. 2022](https://doi.org/10.3390/fire5010024 "Manuscript"). There are over 1,800 homes that have had risk assessments recorded in Ouray County. By training machine learning models to predict these risk scores, we can significantly increase the scale at which WRWC can assess risk. 
5. **Other Data**  
Microsoft Building Footprints for all counties in Colorado were retrieved from UC Boulder's [GeoLibrary](https://geo.colorado.edu/catalog?f%5Bdc_subject_sm%5D%5B%5D=Buildings "Download Building Footprints"). Individual parcel boundaries and Ouray County boundary were obtained online from the [Ouray County GIS Department](https://ouraycountyco.gov/146/GIS-Geographic-Information-Systems-IT "Download Ouray County GIS Data").

## Code in this Repo  
- `r_workflows` primarily handles LAZ files and creating rasters from those files. I converted LAZ files to LAS files. I used the `lidR` package to explore the data and normalize the point clouds. In the `pixel_metrics.rmd` file, I turn the normalized LAS files into rasters that represent forest canopy metrics at 1-meter resolution. 
- `utils` contains packages that I developed, mostly python functions that are packaged logically. Functions include statistics, machine learning model training and testing, and basic raster functions such as reading and writing rasters. 
- `workflows` contains parcel-level risk assessment workflows in python. Primarily Jupyter Notebooks that are well-annotated. These workflows include the full-suite of project tasks from start to finish including handling, exploring, and cleaning the above-mentioned data, which accounts for the bulk of the work in this project. When the data have been cleaned, the building footprints are buffered to create concentric Home Ignition Zones (HIZ). The HIZ polygons are used as analysis areas for the LiDAR rasters. The building locations are intersected with the Global WUI raster to obtain WUI class per building. The tax assessments are appended to each property. All information is appended to the single structure as a feature that is used to create risk score predictions. I use upervised machine learning to predict risk scores. I use unsupervised machine learning to cluster and reduce the dimensionality of the data and create WUI structure archetypes.  