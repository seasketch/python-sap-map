## Algorithm Overview

Assume two people draw areas important to them. Person one draws 2 polygons (in orange), and Person two draws 3 polygons (in green).

![example polygon](img/survey-polygon.png)

Each person has a total value of 100 that they distribute over those areas.

![example polygon with importance](img/survey-polygon-importance.png)

`sapmap` then calculates a Spatial Access Priority value for each polygon:
```
SAP value = importance / area
```

In this example, the polygon with an importance of 10 is 25 square meters per side or 625 square meters in area.  It's SAP value is calculated as:
```
10 / 625 = .016
```

![survey sap map](img/survey-polygon-sap.png)

The polygons are then `rasterized` or 'burned in' to a geospatial raster image (GeoTIFF).  Each pixel in a raster represents a square geographic area of consistent size.

In this example,  The pixels are 25 meters per side.

![survey sap map](img/survey-burn-in.png)

The SAP value of each pixel is then calculated as the sum of the SAP values of the overlapping polygons.  In other words if a polygon overlaps with a pixel, then the SAP value of that polygon is assigned to the pixel.  All of the values for that pixel are then summed together into a final SAP value for that pixel.  This can be displayed as a `heatmap` of importance.

![survey sap map](img/survey-sap-heatmap.png)

The magnitude of the SAP value for each pixel is not important, only its value in relation to other pixels, and the portion of the overall value it represents.

Notice that the polygon that had an importance of 10 yields a pixel with a SAP value of 1.  This is due to it having a relatively large importance for its small area.  The sum of all pixel values is 5, so this one pixel represents 20% of the overall value or importance.