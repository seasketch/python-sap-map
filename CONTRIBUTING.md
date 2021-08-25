## Install source

```
git clone https://github.com/seasketch/heatmap.git
cd heatmap
```

## Start dev container

* Install and start Docker
```
docker-compose build debug
docker-compose run --rm --service-ports heatmap
```

## Run tests

* Install as python package locally (with egg symlink)
```
pip install -e ./
python setup.py test
```

## Debug using VSCode from within container
```
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client examples/simply_sap_map.py
```
* In VSCode, set a breakpoint, Click `Debug` in the left menu, then click `Python Attach` to attach to the waiting process and start it running.

## Installing in OSX

* Install pipenv to your user home directory
pip3 install --user pipenv

* Add user base binary directory to your PATH
/Users/twelch/Library/Python/3.9/bin

```
pip3 install numpy
pip3 install --no-binary fiona rasterio shapely
```

