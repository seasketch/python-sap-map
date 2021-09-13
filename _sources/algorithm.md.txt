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

The polygons are then `rasterized` by overlaying with a grid.  Each cell in the grid represents a geographic area.  In this example, the cells are 25 meters per side.

![survey sap map](img/survey-burn-in.png)

One at a time, each rasterized polygon is 'burned in' to the grid, accumulating its SAP value as an aggregate sum.  In other words if a polygon overlaps with a cell, then the SAP value of that polygon is added to value already in that cell.

The resulting grid is finally output as a geospatial raster image (GeoTIFF), which now represents each grid cell as an image pixel.

![survey sap map](img/survey-sap-heatmap.png)

The magnitude of the SAP value for each pixel is not important, only its value in relation to other pixels, and the portion of the total SAP value it represents.

Notice that the polygon that had an importance of 10 yields a pixel with a SAP value of 1.  This is due to it having a relatively large importance for its small area.  The sum of all pixel values is 5, so this one pixel represents 20% of the overall value or importance.