import math
from rasterio.warp import transform
from rasterio.transform import from_bounds
from rasterio.crs import CRS

def calcRasterProps(inBounds, inCrs, outCrsString, cellSize, boundsPrecision=0):  
  # Start with inBounds and reproject and round if needed
  src_w, src_s, src_e, src_n = inBounds

  if (inCrs['init'] != outCrsString):
    outCrs = CRS.from_string(outCrsString)
    [[src_w, src_e], [src_s, src_n]] = transform(inCrs, outCrs, [src_w, src_e], [src_s, src_n])
  if boundsPrecision > 0:
    src_w, src_s, src_e, src_n = (round(v, boundsPrecision)
      for v in (src_w, src_s, src_e, src_n))

  # Get height and width of dst raster in pixels. Round up to next whole number to ensure coverage
  height = math.ceil((src_n - src_s) / cellSize)
  width = math.ceil((src_e - src_w) / cellSize)

  outBounds = [src_w, src_n - (cellSize * height), src_w + (cellSize * width), src_n]

  # Create transform from raster geographic coordinate space to image pixel coordinate space
  geoToPixel = from_bounds(*outBounds, width, height)

  return (outBounds, width, height, geoToPixel)
