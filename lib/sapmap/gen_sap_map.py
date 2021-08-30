import math
import rasterio
from rasterio.features import bounds, rasterize
from rasterio.enums import MergeAlg
import rasterio.shutil
import fiona
from reprojectFeature import reprojectPolygonFeature
from shapely.geometry import shape
import simplejson
import time
import datetime
from sapmap.calc_raster_props import calcRasterProps
from rasterio.crs import CRS

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
  logfile=None,
  manifestfile=None,
  importanceField=None,
  importanceFactorField=None,
  uniqueIdField=None,
  outCrsString='epsg:3857',
  cellSize=1000,
  boundsPrecision=0,
  fixGeom=False,
  maxArea=None,
  maxSap=None
):
  """Generates Spatial Access Priority (SAP) raster map given run configuration and returns manifest

  infile: path+filename of vector dataset containing features, format must be supported by fiona/gdal
  outfile: path+filename of output raster geotiff
  logfile: path+filename of output logfile
  manifestfile: path+filename of output manifest
  importanceField: name of vector attribute containing importance value used for SAP calculation
  importanceFactorField: name of vector attribute containing importanceFactor value for importance
  uniqueIdField: field containing a unique Id for feature to use for logging the list of features included in the raster for verification.  Must not allow person to be re-identified
  outCrsString: the epsg code for the output raster coordinate system, defaults to epsg:3857 aka Web Mercator
  cellSize: length/width of planning unit in units of output coordinate system, defaults to 1000 (1000m = 1km)
  boundsPrecision: number of digits to round the coordinates of bound calculation to. useful if don't snap to numbers as expected
  fixGeom: if an invalid geometry is found, if fixGeom is True it attempts to fix using buffer(0), otherwise it fails.  Review the log to make sure the automated fix was acceptable
  """
  startTime = time.perf_counter()
  src_shapes = fiona.open(infile)
  outCrs = CRS.from_string(outCrsString)

  manifest = {
    'timestamp': datetime.datetime.now().astimezone().isoformat(),
    'params': {
      'infile': infile,
      'outfile': outfile,
      'logfile': logfile,
      'manifestfile': manifestfile,
      'importanceField': importanceField,
      'importanceFactorField': importanceFactorField,
      'uniqueIdField': uniqueIdField,
      'outCrsString': outCrsString,
      'cellSize': cellSize,
      'boundsPrecision': boundsPrecision,
    },
    'included': [],
    'excluded': [],
    'fixed': []
  }
  log = []

  inBounds = src_shapes.bounds
  (outBounds, width, height, outTransform) = calcRasterProps(src_shapes.bounds, src_shapes.crs, outCrsString, cellSize, boundsPrecision)
  
  areaPerCell = (cellSize * cellSize)

  manifest['height'] = height
  manifest['width'] = width
  manifest['inBounds'] = inBounds
  manifest['outBounds'] = outBounds

  # Generate a list of tuples, each consisting of the geometry and importance, as expected by rasterize
  shapes = []
  for idx, feature in enumerate(src_shapes):
      geometry = feature['geometry'] if src_shapes.crs['init'] == outCrsString else next(reprojectPolygonFeature(feature))
      shapeGeom = shape(geometry)
      error = False
      if not shapeGeom.is_valid:
        if fixGeom:
          fixedGeom = shapeGeom.buffer(0)
          if fixedGeom.is_valid and fixedGeom.area > 0:
            log.append("Fixed invalid feature geometry")
            log.append(simplejson.dumps(feature))
            log.append("With new geometry")
            newGeom = next(reprojectPolygonFeature(fixedGeom.__geo_interface__, "epsg:3857", "epsg:4326"))
            log.append(simplejson.dumps({
              **feature,
              'geometry': newGeom
            }))
            log.append("")     
            shapeGeom = fixedGeom
            if uniqueIdField:
              manifest['fixed'].append(feature['properties'][uniqueIdField])
            else:
              manifest['fixed'].append(idx)
          else:
            error = "Geometry is invalid or area is 0, attempted fix failed" 
      elif shapeGeom.area == 0:
        error = "Area of geometry is zero" 
      elif len(geometry['coordinates'][0]) == 0:
        error = "Geometry has no coordinates"

      if not error:
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
        if uniqueIdField:
          manifest['included'].append(feature['properties'][uniqueIdField])
        else:
          manifest['included'].append(idx)
      elif len(error) > 0:
        log.append("Skipping feature: {}".format(error))
        log.append(simplejson.dumps(feature))
        log.append("")
        if uniqueIdField:
          manifest['excluded'].append(feature['properties'][uniqueIdField])
        else:
          manifest['excluded'].append(idx)

  result = rasterize(
      shapes,
      out_shape=(height, width),
      transform=outTransform,
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
    nodata=0,
    dtype='float32',
    crs=outCrs,
    transform=outTransform,
  ) as out:
    out.write(result, indexes=1)
  
  manifest['includedCount'] = len(manifest['included'])
  manifest['excludedCount'] = len(manifest['excluded'])
  manifest['executionTime'] = round(time.perf_counter() - startTime, 2)

  print('Created SAP raster {} in {}s'.format(outfile, manifest['executionTime']))

  print(' {} features burned in'.format(manifest['includedCount']))
  if manifest['excludedCount'] > 0:
    print(' {} features excluded, see logfile for details'.format(manifest['excludedCount']))
  print('')

  if manifestfile:
    with open(manifestfile, 'w') as manifestFile:
      simplejson.dump(manifest, manifestFile, indent=2)
  else:
      print('Manifest:')
      print(simplejson.dumps(manifest, indent=2))
      print('')

  if logfile:
    with open(logfile, 'w') as logFile:
      for item in log:
          logFile.write("%s\n" % item)
  elif len(log) > 0:
      print('Log:')
      for item in log:
        print(item)
      print('')
  print('')

  return manifest
  


  
