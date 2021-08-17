
=== Installing in Docker

* Install and start Docker

```
git clone https://github.com/seasketch/heatmap.git
cd heatmap
docker-compose run --rm workspace
python -m pip install numpy
python -m pip install --no-binary fiona rasterio shapely
```

=== Installing in OSX

* Install pipenv to your user home directory
pip3 install --user pipenv

* Add user base binary directory to your PATH
/Users/twelch/Library/Python/3.9/bin

```
pip3 install numpy
pip3 install --no-binary fiona rasterio shapely
```

=== Running CLI

```
rio rasterize test.tif --res 0.0167 --property weight < data/passive_rec.geojson
```

