from sapmap import genSapMap
import os.path

runs = [
  {"infile": "../../tests/input/simple-polygon.shp", "outfile": "simple_pure.tif"},
  {"infile": "../../tests/input/simple-polygon.shp", "outfile": "simple_constrained.tif", "maxArea": 10000, "maxSap": 500}
]

for run in runs:
  genSapMap(**run)
