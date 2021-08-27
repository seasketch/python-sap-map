import math
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from rasterio.enums import MergeAlg
import rasterio.shutil
import fiona
from rasterio.warp import transform
from reprojectFeature import reprojectPolygonFeature
from shapely.geometry import shape

def calcSap(geometry, importance=1, areaFactor=1, importanceFactor=1, maxArea=None, maxSap=None):
  """Calculates the SAP value given geometry, its importance, the area per cell, and an optional importanceFactor

  Each respondent has a total SAP of 100, and each shape is assigned a portion
  of that 100 The SAP for a shape is calculated as (Importance / Area), which
  can be interpreted as "importance per area unit".  The area of the shape is
  calculated in the coordinate system used, for Web Mercator that yields
  square meters.  Use the areaFactor option to change this.
  
  Use the optional importanceFactor to accommodate additional variables, changing what the SAP represents.

  Args:
    geometry: Shapely geometry in 3857 (unit of meters)
    importance: importance of geometry (1-100)
    areaFactor: factor to change the area by dividing. For example if area of geometry is calculated in square meters, an areaFactor of 1,000,000 will make the SAP per square km. because 1 sq. km = 1000m x 1000m = 1mil sq. meters
    importanceFactor: numeric value to multiply the importance by.  Use to scale the SAP from being 'per respondent' to a larger group of livelihoods or even economic values 
    maxArea: limits the area of a shape.  Gives shapes with high area an artifically lower one, increasing their SAP relative to others, increasing their presence in heatmap
    maxSap: limits the priority of shapes. Gives shapes with high priority an artificially lower one, decreasing their presence in heatmap
  """
  
  area = geometry.area / areaFactor
  
  if (maxArea):
    area = min(area, maxArea)

  sap = importanceFactor * importance / area

  if (maxSap):
    sap = min(sap, maxSap)
  
  return sap


def genSapMap(
  infile,
  outfile,
  importanceField=None,
  importanceFactorField=None,
  outCrs='epsg:3857',
  cellSize=1000,
  boundsPrecision=0,
  fixGeom=False,
  maxArea=None,
  maxSap=None
):
  """Generates Spatial Access Priority (SAP) raster map given run configuration

  infile: path+filename of vector dataset containing features, format must be supported by fiona/gdal
  outfile: path+filename of output raster geotiff
  importanceField: name of vector attribute containing importance value used for SAP calculation
  importanceFactorField: name of vector attribute containing importanceFactor value for importance
  outCrs: the epsg code for the output raster coordinate system, defaults to epsg:3857 aka Web Mercator
  cellSize: length/width of planning unit in units of output coordinate system, defaults to 1000 (1000m = 1km)
  boundsPrecision: number of digits to round the coordinates of bound calculation to. useful if don't snap to numbers as expected
  fixGeom: if an invalid geometry is found, if fixGeom is True it attempts to fix using buffer(0), otherwise it fails.  Review the log to make sure the automated fix was acceptable
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
  areaPerCell = (cellSize * cellSize)

  # Transform shapes to a list of tuples, each consisting of (geometry in Web Mercator CRS, importance).  This is the input shape expected by rasterize
  shapes = []
  for feature in src_shapes:
      geometry = feature['geometry'] if src_shapes.crs['init'] == outCrs else reprojectPolygonFeature(feature)      
      shapeGeom = shape(geometry)
      if not shapeGeom.is_valid:

        # TODO: test invalid shapes

        if fixGeom:
          fixedGeom = shapeGeom.buffer(0)
          print("Fixed geometry")
          print(fixedGeom)
          shapeGeom = fixedGeom
        else:
          print(geometry)
          raise Exception("Invalid geometry found, use fixGeom=True if you want an automated fix to be attempted")

      # TODO: check for missing importanceField if provided
      # TODO: check for missing importanceFactorField if provided

      shapes.append((
        geometry,
        calcSap(
          shapeGeom,
          feature['properties'][importanceField] if importanceField else 1,
          areaPerCell,
          feature['properties'][importanceFactorField] if importanceFactorField else 1,
          maxArea,
          maxSap
        )
      ))

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