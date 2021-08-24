"""$ python gen_heatmap input.shp output.tif"""

import math
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from rasterio.enums import MergeAlg
import rasterio.shutil
import fiona
from rasterio.warp import transform

# TODO: support user-defined filter
# TODO: support geojson
# TODO: support user provided raster with planning units
# TODO: handle other preprocessing done elsewhere

class RunConfig(object):
    cellSize = 100
    infile = './input.shp'
    outfile = './output.tif'
    importanceField = 'weight'
    maxArea = None
    maxSap = None

    def __init__(self, dictionary):
        self.__dict__.update(dictionary)

runs = [
  {'infile': "data/passive_rec.shp", 'outfile': './outputPure.tif'},
  {'infile': "data/passive_rec.shp", 'outfile': './outputConstrained.tif', 'maxArea': 10000, 'maxSap': 500}
]

def calcSap(geometry, importance, cellSize, maxArea = None, maxSap = None):
  """Calculates the SAP value given geometry and its importance

  Each respondent has a total SAP of 100, and each shape is assigned a portion of that 100
  The SAP for a shape is calculated as (Importance / Area) where Area is relative to planning unit size
  Once all shapes are summed, a cell with a SAP of 10 for example, represents a tenth of a respondent

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
  areaPerCell = (cellSize * cellSize) # area of single raster cell
  area = shape.area / areaPerCell # shape area, in units of area per cell, which also yields the total number of cells
  
  if (maxArea):
    area = min(area, maxArea)

  sap = importance / area

  if (maxSap):
    sap = min(sap, maxSap)
  
  return sap

def feature_to_mercator(feature):
  """Normalize feature and converts coords to 3857.

  Args:
    feature: geojson feature to convert to mercator geometry.
  """
  # Ref: https://gist.github.com/dnomadb/5cbc116aacc352c7126e779c29ab7abe

  src_crs = CRS.from_epsg(4326)
  dst_crs = CRS.from_epsg(3857)

  geometry = feature["geometry"]
  if geometry["type"] == "Polygon":
      xys = (zip(*part) for part in geometry["coordinates"])
      xys = (list(zip(*transform(src_crs, dst_crs, *xy))) for xy in xys)

      yield {"coordinates": list(xys), "type": "Polygon"}

  elif geometry["type"] == "MultiPolygon":
      for component in geometry["coordinates"]:
          xys = (zip(*part) for part in component)
          xys = (list(zip(*transform(src_crs, dst_crs, *xy))) for xy in xys)

          yield {"coordinates": list(xys), "type": "Polygon"}

def genSap(run):
  """Generates Spatial Access Priority (SAP) raster given run configuration
  """
  config = RunConfig(run)
  src_crs = CRS.from_epsg(4326)
  dst_crs = CRS.from_epsg(3857)

  src_geometries = fiona.open(config.infile)

  # Alternative is to use study region or user supplied bounds
  minx, miny, maxx, maxy = src_geometries.bounds

  [[dst_minx, dst_maxx], [dst_miny, dst_maxy]] = transform(src_crs, dst_crs, [minx, maxx], [miny, maxy])
  bounds = [dst_minx, dst_miny, dst_maxx, dst_maxy]
  
  # TODO: this doesn't align with 100m cell size, need to calc new max
  height = math.ceil((dst_maxy - dst_miny) / config.cellSize)
  width = math.ceil((dst_maxx - dst_minx) / config.cellSize)

  # Generate list of tuples, each consisting of geometry in Web Mercator and its importance.  This is the input shape expected by rasterize
  shapes = [(geometry, calcSap(geometry, feature['properties'][config.importanceField], config.cellSize, config.maxArea, config.maxSap)) for feature in src_geometries for geometry in feature_to_mercator(feature)]

  # Create transform from raster geographic coordinate space to image pixel coordinate space
  geoToPixel = from_bounds(*bounds, width, height)

  result = rasterize(
      shapes,
      out_shape=(height, width),
      transform=geoToPixel,
      merge_alg=MergeAlg.add,
      fill=0
  )

  with rasterio.open(
    config.outfile,
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

for run in runs:
  genSap(run)