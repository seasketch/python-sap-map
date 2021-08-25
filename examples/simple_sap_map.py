from sapmap import genSap, RunConfig
import os.path

runs = [
  {"infile": "../tests/input/passive_rec.shp", "outfile": "simple_pure.tif"},
  {"infile": "../tests/input/passive_rec.shp", "outfile": "simple_constrained.tif", "maxArea": 10000, "maxSap": 500}
]

for run in runs:
    config = RunConfig(run)
    assert(os.path.isfile(config.infile))
    genSap(config)
    assert(os.path.isfile(config.outfile))
