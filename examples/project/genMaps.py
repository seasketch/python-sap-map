from sapmap import genSapMap
import os.path

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

runs = []
for infile in input:
    runs.append({
        "infile": "input/{}".format(infile),
        "outfile": "output/{}.tif".format(infile.split('.')[0]),
        "logfile": "output/{}.log.txt".format(infile.split('.')[0]),
        "manifestfile": "output/{}.manifest.json".format(infile.split('.')[0]),
        "cellSize": 100,
        "uniqueIdField": "id",
        "fixGeom": True
    })

for run in runs:
  genSapMap(**run)
