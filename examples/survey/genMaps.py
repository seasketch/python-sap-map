from sapmap import genSapMap

resolution = 25
pixelArea = (resolution * resolution)

runs = [
  {
    "infile": "input/example-survey.geojson",
    "outfile": "output/example-survey.tif",
    "outResolution": resolution,
    "areaFactor": pixelArea
  }
]

for run in runs:
  genSapMap(**run)
