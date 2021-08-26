import math
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from rasterio.enums import MergeAlg
import rasterio.shutil
import fiona
from rasterio.warp import transform
from featureToMercator import feature_to_mercator
from shapely.geometry import shape

def calcSap(geometry, importance, cellSize, maxArea = None, maxSap = None):
  """Calculates the SAP value given geometry and its importance

  Each respondent has a total SAP of 100, and each shape is assigned a portion of that 100
  The SAP for a shape is calculated as (Importance / Area), which can be
  interpreted as "importance per area unit". By default the unit of area of the
  shape is that of the coordinate system used, for Web Mercator that is 1 square meter.
  
  Variations:
  * SAP = ((Crew * Importance) / Area) - multiplying the importance by a factor of crew size.  Could also be landing data, etc.
  * Weighted SAP = SAP * Weighting(W) - upscaling a sample to represent an entire group.  W = (total estimated / total sampled)

  Args:
    geometry: geometry in 3857 (unit of meters)
    importance: importance of geometry (1-100)
    cellSize: the length of each cell side
    maxArea: limits the area of a shape.  Gives shapes with high area an artifically lower one, increasing their SAP relative to others, increasing their presence in heatmap
    maxSap: limits the priority of shapes. Gives shapes with high priority an artificially lower one, decreasing their presence in heatmap
  """
  
  shapeGeom = shape(geometry)
  areaPerCell = (cellSize * cellSize)
  
  """
  Scale from the spatial unit of the coordinate system to one raster cell.
  
  By doint that, it makes the SAP value more understandable. If a shape then
  has a SAP of 10, we can say it represents a tenth of a respondent per
  raster cell, because each respondent has a total SAP of 100.
  """
  area = shapeGeom.area / areaPerCell
  
  if (maxArea):
    area = min(area, maxArea)

  sap = importance / area

  if (maxSap):
    sap = min(sap, maxSap)
  
  return sap


def genSapMap(
  infile,
  outfile,
  importanceField='weight',
  outCrs='epsg:3857',
  cellSize=100,
  boundsPrecision=0,
  maxArea=None,
  maxSap=None
):
  """Generates Spatial Access Priority (SAP) raster given run configuration

  infile: path+filename of vector dataset containing features, format must be supported by fiona/gdal
  outfile: path+filename of output raster geotiff
  importanceField: name of vector attribute containing importance value used for SAP calculation
  outCrs: the epsg code for the output raster coordinate system
  cellSize: size of cells in units of output coordinate system
  boundsPrecision: number of digits to round bound coordinates to
  """
  dst_crs = CRS.from_string(outCrs)

  src_shapes = fiona.open(infile)

  # Start with src bounds and reproject and round if needed
  src_w, src_s, src_e, src_n = src_shapes.bounds
  
  if (src_shapes.crs['init'] != outCrs):
    [[src_w, src_e], [src_s, src_n]] = transform(src_shapes.crs, dst_crs, [src_w, src_e], [src_s, src_n])
  if boundsPrecision > 0:
    src_w, src_s, src_e, src_n = (round(v, boundsPrecision)
      for v in (src_w, src_s, src_e, src_n))

  # Get height and width of dst raster in pixels. Round up to next whole number to ensure coverage
  height = math.ceil((src_n - src_s) / cellSize)
  width = math.ceil((src_e - src_w) / cellSize)

  dstBounds = [src_w, src_n - (cellSize * height), src_w + (cellSize * width), src_n]

  # Generate list of tuples, each consisting of geometry in Web Mercator and its importance.  This is the input shape expected by rasterize
  shapes = [(geometry, calcSap(geometry, feature['properties'][importanceField], cellSize, maxArea, maxSap)) for feature in src_shapes for geometry in feature_to_mercator(feature)]

  # Create transform from raster geographic coordinate space to image pixel coordinate space
  geoToPixel = from_bounds(*dstBounds, width, height)

  result = rasterize(
      shapes,
      out_shape=(height, width),
      transform=geoToPixel,
      merge_alg=MergeAlg.add,
      fill=0
  )

  with rasterio.open(
    outfile,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='float32',
    crs=dst_crs,
    transform=geoToPixel,
  ) as out:
    out.write(result, indexes=1)