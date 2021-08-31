#!/usr/bin/env python 
# Usage: genMask cell_size, [w,s,e,n]

import rasterio
import fiona
from rasterio.features import geometry_mask
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from sapmap.calc_raster_props import calcRasterProps
from rasterio.crs import CRS
import sys
import numpy as np
import numpy.distutils.system_info as sysinfo

eezFile = 'base/eez_selection_3857.shp'
landFile = 'base/land_selection_3857.shp'
outFile = 'output/mask.tif'

eezSearchProperty = "UNION"
eezSearchValue = "Bermuda"
landSearchProperty = "FID"
landSearchValue = 330955

cellSize = 5000
outCrsString='epsg:3857'
outCrs = CRS.from_string(outCrsString)

# Get single dissolved feature to create mask with
eezLandFeatures = fiona.open(eezFile)
eezProperties, eezGeom = zip(*[(feature['properties'], shape(feature['geometry'])) for feature in eezLandFeatures])
eezDissolved = ({'geometry': mapping(unary_union(eezGeom)), 'properties': eezProperties[0]})

landFeatures = fiona.open(landFile)
landProperties, landGeom = zip(*[(feature['properties'], shape(feature['geometry'])) for feature in landFeatures])
landDissolved = ({'geometry': mapping(unary_union(landGeom)), 'properties': landProperties[0]})

# Calculate out raster props from from eez feature
inBounds = shape(eezDissolved['geometry']).bounds
(outBounds, width, height, outTransform) = calcRasterProps(inBounds, eezLandFeatures.crs, outCrsString, cellSize)

# NOT WORKING - need to verify need

# Option 1
# output raster mask - 1 is mask
# use np.where to apply mask (https://stackoverflow.com/questions/49453930/return-masked-array-as-simple-array-with-masked-values-as-none)

# Create initial 2D array of zeros
outArray = np.zeros((height, width), np.float32)

eez_array = rasterio.features.rasterize(
    [(eezDissolved['geometry'], 1)], # 
    out_shape=(height, width),
    transform=outTransform,
    fill=0,
    dtype='uint8')
eez_array = eez_array.astype(bool)
with rasterio.open(
    'output/eez_mask_test.tif',
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='float32',
    crs=outCrs,
    transform=outTransform,
    ) as out:
    out.write(eez_array, indexes=1)

land_array = rasterio.features.rasterize(
    [(landDissolved['geometry'], 1)],
    out_shape=(height, width),
    transform=outTransform,
    fill=0,
    dtype='uint8')
land_array = land_array.astype(bool)
with rasterio.open(
    'output/land_mask_test.tif',
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='float32',
    crs=outCrs,
    transform=outTransform,
    ) as out:
    out.write(land_array, indexes=1)

mask_array = np.logical_and(~eez_array, land_array)

# Mask land and everything outside of eez
masked = np.ma.MaskedArray(
    zeroArray,
    mask=(land_array | ~eez_array)
)

with rasterio.open(
    outFile,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    nodata=0,
    dtype='float32',
    crs=outCrs,
    transform=outTransform,
    ) as out:
    out.write(masked, indexes=1)