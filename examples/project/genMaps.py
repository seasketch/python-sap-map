from sapmap import genSapMap
import os.path
import time

input = [
    "Aquaculture_Area.shp",
    "Boating_Area.shp",
    "Commercial_Fishing_Area.shp",
    "Other_Area.shp",
    "Passive_Recreation___Conservation_Area.shp",
    "Recreational_Fishing_Area.shp",
    "Shipping_Area.shp",
    "Tourism_Area.shp",
    "Utilities_Area.shp"
]

eez_bounds = [ -68.9170557997853, 28.9057705996336, -60.7047988004242, 35.8085514002271 ]

runs = []
for infile in input:
    runs.append({
        "infile": "input/{}".format(infile),
        "outfile": "output/{}.tif".format(infile.split('.')[0]),
        "logfile": "output/{}.log.txt".format(infile.split('.')[0]),
        "manifestfile": "output/{}.manifest.json".format(infile.split('.')[0]),
        "outResolution": 100,
        "bounds": eez_bounds,
        "uniqueIdField": "id",
        "fixGeom": True
    })

startTime = time.perf_counter()
for run in runs:
  genSapMap(**run)
print("Execution time: {}".format(round(time.perf_counter() - startTime, 2)))
