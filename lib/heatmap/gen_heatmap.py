import math
import os
from numpy import Infinity
import rasterio
from rasterio.features import bounds, rasterize
from rasterio.enums import MergeAlg
from rasterio.crs import CRS
import rasterio.shutil
from reprojectFeature import reprojectPolygon
from shapely.geometry import shape, box, Polygon
import fiona
import simplejson
import time
import datetime
from heatmap.calc_raster_props import calcRasterProps
from heatmap.calc_sap import calcSap

def genHeatMap(
  infile,
  outPath=None,
  overwrite=False,
  method='sap',
  importanceField=None,
  importanceFactorField=None,
  areaFactor=1,
  uniqueIdField=None,
  outCrsString='epsg:3857',
  outResolution=1000,
  bounds=None,
  boundsPrecision=0,
  allTouchedSmall=False,
  allTouchedSmallFactor=1.25,
  fixGeom=False,
  maxArea=None,
  maxSap=None,
  logToFile=False,
):
  """Generates Spatial Access Priority (SAP) raster map given run configuration

  Arguments:
    infile: path+filename of vector dataset containing features, format must be supported by fiona/gdal
    outpath: path to output heatmaps to.  Filename will be the same as the input, just with the .tif extension.  If not specified, heatmaps are output to the input folder
    overwrite: whether to overwrite existing heatmap output, defaults to false and skips
    method: method for calculating value: count, area, sap. Defaults to area
    importanceField: name of vector attribute containing importance value used for SAP calculation
    importanceFactorField: name of vector attribute containing importanceFactor value for importance
    areaFactor: factor to change the area by dividing. For example if area of geometry is calculated in square meters, an areaFactor of 1,000,000 will make the SAP per square km. because 1 sq. km = 1000m x 1000m = 1mil sq. meters 
    uniqueIdField: field containing a unique Id for feature to use for logging the list of features included in the raster for verification.  Must not allow person to be re-identified
    outCrsString: the epsg code for the output raster coordinate system, defaults to epsg:3857 aka Web Mercator
    outResolution: length/width of planning unit in units of output coordinate system, defaults to 1000 (1000m = 1km)
    bounds: bounds to use for output raster, as [w, s, e, n] in CRS of infile.  Output raster will align to the top left, but will extend past the bottom right as needed to the next multiple of outResolution
    boundsPrecision: number of digits to round the coordinates of bound calculation to. useful if don't snap to numbers as expected
    allTouchedSmall: (boolean) use allTouched rasterize option for shapes with smaller shape index than a raster cell (area/perimeter length).  Ensures small and narrow shapes are not lost and every shape contributes heat to at least one pixel in result. Larger shapes are still picked up using Bresenham’s line algorithm because allTouched creates some seemingly invalid output (double counting) along shape boundaries. Using allTouched only for smallest shapes that need it mitigates this, but also uses additional memory, and will also carry more weight than shapes just above the index threshold.
    allTouchedSmallFactor: (number) use to increase the shapeIndex threshold for identifying small shapes.  shapeIndex threshold is calculated as (shapeIndex of a raster cell * allTouchedSmallFactor).  Defaults to 1.25.  Increasing the factor will identify increasingly larger shapes as "small" and to be run with AllTouched option.  Useful when you have polygons that are mostly large but have small areas that are long and narrow and thus spotty in being picked up
    fixGeom: if an invalid geometry is found, if fixGeom is True it attempts to fix using buffer(0), otherwise it fails.  Review the log to make sure the automated fix was acceptable
    logToFile: (boolean) whether to output logs, errors, and manifest to file or stdout

  Returns:
    Manifest of run
  """
  startTime = time.perf_counter()
  
  try:
    src_shapes = fiona.open(infile)
  except (fiona.errors.DriverError):
    print('Warning: infile not found, skipping {0}'.format(infile))
    return None

  if len(src_shapes) < 1:
    print('Warning: infile contains no features, skipping {0}'.format(infile))
    return None
  
  outCrs = CRS.from_string(outCrsString)
  error_shapes = []

  # output files have the same name as infile
  inpath, inFullFilename = os.path.split(infile)
  inFilename = inFullFilename.split('.')[0]
  # full path, minus extension
  inBasename = ''

  if outPath is None:
    inBasename = os.path.join(inpath, inFilename)    
  else:
    inBasename = os.path.join(outPath, inFilename)

  outfile = "{}.tif".format(inBasename)
  outfileSmall = "{}_small.tif".format(inBasename)
  outfileLarge = "{}_large.tif".format(inBasename)
  logfile = "{}.log.txt".format(inBasename) if logToFile else None
  manifestfile = "{}.manifest.json".format(inBasename) if logToFile else None
  errorfile = "{}.error.geojson".format(inBasename) if logToFile else None

  if os.path.exists(outfile) and not overwrite:
    print('Warning: outfile {0} already exists, skipping. Remove it and re-run or use overwrite option'.format(outfile))
    return None
  elif os.path.exists(outfile) and overwrite:
    print('Overwriting {0} '.format(outfile))

  manifest = {
    'timestamp': datetime.datetime.now().astimezone().isoformat(),
    'params': {
      'infile': infile,
      'outfile': outfile,
      'logfile': logfile,
      'manifestfile': manifestfile,
      'errorfile': errorfile,
      'importanceField': importanceField,
      'importanceFactorField': importanceFactorField,
      'uniqueIdField': uniqueIdField,
      'outCrsString': outCrsString,
      'outResolution': outResolution,
      'bounds': bounds,
      'boundsPrecision': boundsPrecision,
      'allTouchedSmall': allTouchedSmall,
    },
    'included': [],
    'includedSmall': [],
    'excluded': [],
    'fixed': [],
    'includedCount': 0,
    'excludedCount': 0,
    'includedSmallCount': 0
  }
  log = []

  inBounds = bounds if bounds else src_shapes.bounds
  (outBounds, width, height, outTransform) = calcRasterProps(inBounds, src_shapes.crs, outCrsString, outResolution, boundsPrecision)  

  manifest['height'] = height
  manifest['width'] = width
  manifest['inBounds'] = inBounds
  manifest['outBounds'] = outBounds

  # Generate a list of tuples, each consisting of the geometry and importance, as expected by rasterize
  shapes = []
  # Special handle shapes smaller than an output pixel
  smallShapes = []

  # Get shape index for one output raster cell
  (minx, miny, maxx, maxy) = inBounds
  cellBL = (minx, miny)
  cellBR = (minx + outResolution, miny)
  cellTR = (minx + outResolution, miny + outResolution)
  cellTL = (minx, miny + outResolution)
  cellPoly = Polygon([cellBL, cellBR, cellTR, cellTL, cellBL])
  # Based on https://gis.stackexchange.com/questions/316128/identifying-long-and-narrow-polygons-in-with-postgis
  # In practice, the inverse method does not seem to work as well
  cellShapeIndex = cellPoly.area / cellPoly.length

  minShapeIndex = Infinity
  maxShapeIndex = 0
  shapeIndexThreshold = Infinity

  if allTouchedSmall:
    shapeIndexThreshold = cellShapeIndex * allTouchedSmallFactor

  for idx, feature in enumerate(src_shapes):
      geometry = feature['geometry'] if src_shapes.crs['init'] == outCrsString else next(reprojectPolygon(feature))
      shapeGeom = shape(geometry)
      error = False
      if not shapeGeom.is_valid:
        if fixGeom:
          fixedGeom = shapeGeom.buffer(0)
          if fixedGeom.is_valid and fixedGeom.area > 0:
            log.append("Fixed invalid feature geometry")
            log.append(simplejson.dumps(feature))
            log.append("With new geometry")
            newGeom = next(reprojectPolygon(fixedGeom.__geo_interface__, "epsg:3857", "epsg:4326"))
            log.append(simplejson.dumps({
              **feature,
              'geometry': newGeom
            }))
            log.append("")     
            shapeGeom = fixedGeom
            if uniqueIdField:
              manifest['fixed'].append(feature['properties'][uniqueIdField])
            else:
              manifest['fixed'].append(idx + 1)
          else:
            error = "Geometry is invalid or area is 0, attempted fix failed" 
            error_shapes.append(feature)
        else:
            error = "Geometry is invalid"
            error_shapes.append(feature)
      elif shapeGeom.area == 0:
        error = "Area of geometry is zero" 
      elif len(geometry['coordinates'][0]) == 0:
        error = "Geometry has no coordinates"

      if not error:
        heatValue = 1 # count method
        if method == 'area':
          heatValue = 1 / shapeGeom.area
        elif method == 'sap':
          heatValue = calcSap(
              shapeGeom,
              feature['properties'][importanceField] if importanceField else 1,
              areaFactor,
              feature['properties'][importanceFactorField] if importanceFactorField else 1,
              maxArea,
              maxSap
            )

        curShapeIndex = 0
        if allTouchedSmall:
          curShapeIndex = shapeGeom.area / shapeGeom.exterior.length
          minShapeIndex = min(minShapeIndex, curShapeIndex)
          maxShapeIndex = max(maxShapeIndex, curShapeIndex)
        isSmall = allTouchedSmall and curShapeIndex < shapeIndexThreshold
        if (isSmall):
          smallShapes.append((
            geometry,
            heatValue
          ))
        else:
          shapes.append((
            geometry,
            heatValue
          ))

        if uniqueIdField:
          manifest['included'].append(feature['properties'][uniqueIdField])
          if isSmall:
            manifest['includedSmall'].append(feature['properties'][uniqueIdField])
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

  result = None
  if allTouchedSmall and len(smallShapes) > 0:
    result = rasterize(
        smallShapes,
        out_shape=(height, width),
        transform=outTransform,
        merge_alg=MergeAlg.add,
        fill=0,
        all_touched=True
    )
    # Debug - output small shape raster
    # if result is not None:
    #   with rasterio.open(
    #     outfileLarge,
    #     'w',
    #     driver='GTiff',
    #     height=height,
    #     width=width,
    #     count=1,
    #     nodata=0,
    #     dtype='float32',
    #     crs=outCrs,
    #     transform=outTransform
    #   ) as out:
    #     out.write(result, indexes=1)

  if len(shapes) > 0:
    if result is not None and result.size > 0:
      result = result + rasterize(
        shapes,
        out_shape=(height, width),
        transform=outTransform,
        merge_alg=MergeAlg.add,
        fill=0,
        all_touched=False
      )
    else:
      result = rasterize(
        shapes,
        out_shape=(height, width),
        transform=outTransform,
        merge_alg=MergeAlg.add,
        fill=0,
        all_touched=False
      )
      # Debug - output small shape raster
      # if result is not None:
      #   with rasterio.open(
      #     outfileLarge,
      #     'w',
      #     driver='GTiff',
      #     height=height,
      #     width=width,
      #     count=1,
      #     nodata=0,
      #     dtype='float32',
      #     crs=outCrs,
      #     transform=outTransform
      #   ) as out:
      #     out.write(result, indexes=1)

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
    transform=outTransform
  ) as out:
    out.write(result, indexes=1)

  manifest['includedCount'] = len(manifest['included'])
  manifest['excludedCount'] = len(manifest['excluded'])
  manifest['executionTime'] = round(time.perf_counter() - startTime, 2)
  if allTouchedSmall:
    manifest['includedSmallCount'] = len(smallShapes)
    manifest['cellShapeIndex'] = cellShapeIndex
    manifest['allTouchedSmallFactor'] = allTouchedSmallFactor
    manifest['shapeIndexThreshold'] = shapeIndexThreshold

  print('Created SAP raster {} in {}s'.format(outfile, manifest['executionTime']))

  print(' {} features burned in'.format(manifest['includedCount']))
  if (allTouchedSmall):
    print(' allTouchedSmall enabled, numSmallShapes: {0}'.format(len(smallShapes)))
    print('  cellShapeIndex: {0}, shapeIndexThreshold: {1} minShapeIndex: {2}, maxShapeIndex: {3}'.format(cellShapeIndex, shapeIndexThreshold, minShapeIndex, maxShapeIndex))
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



  if errorfile and len(error_shapes) > 0:
    with open(errorfile, 'w') as errorFile:
      errorFile.write(simplejson.dumps({
        "type": "FeatureCollection",
        "features": error_shapes
      }))

  return manifest
  


  
