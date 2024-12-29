# Exploring seasonal dynamics of Landsat 8 and 9 data on vegetation indices

Vegetation indices are key measures to access the different aspects of the vegetation like its health, growth, potential yield estimation in the case of crops, and so on. With the new satellite Landsat-9 (L9) having significant improvement in radiometric resolution over Landsat-8 (L8), it is very mandatory to monitor the changes that come up with new sensors and finer temporal resolution. A comparison of two satellites is done concerning different four vegetation indices seasonally within the year 2022 using different evaluation metrics as well as performance over different land use categories is also evaluated. Out of four seasons, summer followed by winter, spring, and fall has more deviation of L8 data concerning L9 was found. Examining the correlation of different vegetation indices between two satellites in each season, fall has the strongest correlation (average 0.98 R2) whereas summer has the least correlation on comparison (average of 0.85 R2).

## Vegetation Index 

### NDVI (Normalized Difference Vegetation Index)

NDVI is a measure of vegetation greenness or density. It is calculated using the formula:

NDVI = (NIR - Red) / (NIR + Red)

Where NIR (Near-Infrared) and Red are reflectance values from corresponding bands.

### EVI (Enhanced Vegetation Index)
EVI enhances the sensitivity of vegetation index calculations to canopy structural variations and atmospheric conditions. It is calculated as:
EVI = G * ((NIR - Red) / (NIR + C1 * Red - C2 * Blue + L))

### NDWI (Normalized Difference Water Index)
NDWI is used to highlight water bodies and is calculated using:
NDWI = (Green - NIR) / (Green + NIR)

### Study Area
For this study, one small study area with 70.5 Km2   is selected for the cross-comparison. The area is located in the Terai region of Nepal which includes diverse land use. It includes small sections of two local administrative boundaries: Nawalparasi East and Chitwan districts.
<img src="https://github.com/supathdhitalGEO/Vegetation_Indices/blob/main/Image/StudyArea.jpg"/>

### WorkFlow
The complete graphical methodology followed in this research is shown in the chart below. 
<img src="https://github.com/supathdhitalGEO/Vegetation_Indices/blob/main/Image/Workflow_Diagram.png"/>

### Correlation between the vegetation indices in different seasons
<img src = "https://github.com/supathdhitalGEO/Vegetation_Indices/blob/main/Image/vegetation_correlation1.png"/>

### Evaluation Metrics
<img src  = "https://github.com/supathdhitalGEO/Vegetation_Indices/blob/main/Image/evaluationmetrics.png"/>

### Evaluation metrics of different land use classes
<img src = "https://github.com/supathdhitalGEO/Vegetation_Indices/blob/main/Image/radar_chart.png"/>



