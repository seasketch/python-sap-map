import math
import rasterio
from rasterio.features import bounds, rasterize
from rasterio.enums import MergeAlg
import rasterio.shutil
import fiona
from reprojectFeature import reprojectPolygon
from shapely.geometry import shape
import simplejson
import time
import datetime
from sapmap.calc_raster_props import calcRasterProps
from sapmap.calc_sap import calcSap
from rasterio.crs import CRS

def genSapMap(
  infile,
  outfile,
  logfile=None,
  manifestfile=None,
  importanceField=None,
  importanceFactorField=None,
  uniqueIdField=None,
  outCrsString='epsg:3857',
  outResolution=1000,
  bounds=None,
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
  outResolution: length/width of planning unit in units of output coordinate system, defaults to 1000 (1000m = 1km)
  bounds: bounds to use for output raster, as [w, s, e, n] in CRS of infile.  Output raster will align to the top left, but will extend past the bottom right as needed to the next multiple of outResolution
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
      'outResolution': outResolution,
      'bounds': bounds,
      'boundsPrecision': boundsPrecision,
    },
    'included': [],
    'excluded': [],
    'fixed': []
  }
  log = []

  inBounds = bounds if bounds else src_shapes.bounds
  (outBounds, width, height, outTransform) = calcRasterProps(inBounds, src_shapes.crs, outCrsString, outResolution, boundsPrecision)
  areaPerCell = (outResolution * outResolution)

  manifest['height'] = height
  manifest['width'] = width
  manifest['inBounds'] = inBounds
  manifest['outBounds'] = outBounds

  # Generate a list of tuples, each consisting of the geometry and importance, as expected by rasterize
  shapes = []
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
  


  
