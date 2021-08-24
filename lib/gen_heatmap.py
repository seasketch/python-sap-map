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

CELL_SIZE = 100
src_crs = CRS.from_epsg(4326)
dst_crs = CRS.from_epsg(3857)
src_geometries = fiona.open("../data/passive_rec.shp")

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

# Alternative is to use study region
minx, miny, maxx, maxy = src_geometries.bounds
[[dst_minx, dst_maxx], [dst_miny, dst_maxy]] = transform(src_crs, dst_crs, [minx, maxx], [miny, maxy])
bounds = [dst_minx, dst_miny, dst_maxx, dst_maxy]

features = []
shapes = []
crs = None
with fiona.collection("../data/passive_rec.shp", "r") as source:
    shapes = [(geometry, feature['properties']['weight']) for feature in source for geometry in feature_to_mercator(feature)]

# PROBLEM: this doesn't align with 100m cell size, need to work backwards
height = math.ceil((dst_maxy - dst_miny) / CELL_SIZE)
width = math.ceil((dst_maxx - dst_minx) / CELL_SIZE)

transform = from_bounds(*bounds, width, height)

result = rasterize(
    shapes,
    out_shape=(height, width),
    transform=transform,
    merge_alg=MergeAlg.add,
    default_value=0,
    fill=-1
)

with rasterio.open(
    '../data/output.tif',
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='float32',
    crs=dst_crs,
    transform=transform,
) as out:
    out.write(result, indexes=1)
