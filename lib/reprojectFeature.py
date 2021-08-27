from rasterio.crs import CRS
from rasterio.warp import transform

def reprojectPolygonFeature(feature, outCrs='epsg:3857'):
  """Reproject Polygon/MultiPolygon to a different coordinate system.

  Args:
    feature: geojson feature to convert to mercator geometry.
    outCrs: coordinate system to reproject to, as epsg string.  Defaults to 'epsg:3857'
  """
  # Ref: https://gist.github.com/dnomadb/5cbc116aacc352c7126e779c29ab7abe

  src_crs = CRS.from_epsg(4326)
  dst_crs = CRS.from_string(outCrs)

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