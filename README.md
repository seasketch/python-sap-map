
=== Install
```
git clone https://github.com/seasketch/heatmap.git
cd heatmap
```

=== Start 

* Install and start Docker
```
docker-compose build debug
docker-compose run --rm --service-ports heatmap
```


=== Debug using VSCode from within container
```
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client lib/hello.py
```
* In VSCode, set a breakpoint, Click `Debug` in the left menu, then click `Python Attach` to attach to the waiting process and start it running.

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

