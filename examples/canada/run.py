from sapmap import genSapMap
import os.path
import time

input = [
    "testPolygons.geojson"
]

eez_bounds = [ -141.002725124365, 40.0511489973286, -47.6941470240656, 86.4318731326392 ]

resolution = 350
pixelArea = (resolution * resolution)

runs = []
for infile in input:
    runs.append({
        "infile": "input/{}".format(infile),
        "outfile": "output/{}.tif".format(infile.split('.')[0]),
        "logfile": "output/{}.log.txt".format(infile.split('.')[0]),
        "manifestfile": "output/{}.manifest.json".format(infile.split('.')[0]),
        "errorfile": "output/{}.error.geojson".format(infile.split('.')[0]),
        "outResolution": resolution,
        "bounds": eez_bounds,
        "areaFactor": pixelArea,
        "uniqueIdField": "id",
        "fixGeom": True,
        "allTouched": False
    })

startTime = time.perf_counter()
for run in runs:
  genSapMap(**run)
print("Execution time: {}".format(round(time.perf_counter() - startTime, 2)))
