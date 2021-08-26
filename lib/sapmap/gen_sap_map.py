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

def calcSap(geometry, importance, cellSize, maxArea = None, maxSap = None):
  """Calculates the SAP value given geometry and its importance

  Each respondent has a total SAP of 100, and each shape is assigned a portion of that 100
  The SAP for a shape is calculated as (Importance / Area)

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
  from shapely.geometry import shape

  shape = shape(geometry)
  
  """
  The SAP value (Importance / Area) can be interpreted as "importance per area unit".
  We want to scale the area to a unit of area that makes sense.  By default it will be that
  of the coordinate system, for Web Mercator that is 1m^2.
  
  We want to scale it to the area of one raster cell.  That way if a shape has a
  SAP of 10, then we can say it represents a tenth of a respondent per cell,
  because each respondent has a total SAP of 100.
  """
  areaPerCell = (cellSize * cellSize)
  area = shape.area / areaPerCell
  
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