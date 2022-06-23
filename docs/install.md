# Installation and Usage

A Docker recipe is available to install `sapmap` in an isolated virtual environment on your local computer with all dependencies.  In the future, a published module may be made available.

1. First install and start [Docker Desktop](https://www.docker.com/) on your local computer.  Windows, MacOS, Linux are all supported.

2. Clone the code, build a docker image, run a container with the image and open a shell to it, run final sap setup, then run the test suite to verify it's working:
```bash
    git clone https://github.com/seasketch/python-sap-map.git
```

3. Build docker image (only need to run once)
```bash
    cd python-sap-map
    docker-compose build sapmap
```

4. Start the container.
```bash
    docker-compose run --rm --service-ports sapmap
```
With this basic start command, the container only has access to the python-sap-map folder so any input/output will need to be maintained within it.

1. Alternatively, start container with external folder mounts for input and output
```bash
docker-compose run --rm --service-ports -v /absolute/path/to/input:/work/input -v /absolute/path/to/output:/work/output  sapmap
```
With these volume mounts, config.json files can load shapes via `infile: '/work/input/my_shapes.shp`.  And `outpath: /work/output` can be used to write heatmaps back out of the container.

6. Optionally, verify everything installed correctly.
```bash
    pytest
```

## Example Projects

Multiple example projects are included that can be run out of the box.

`Simple` - small geographic extent.  Very simple test dataset with polygons that aligned to 100m boundaries for ease of interpreting the result.  Produces raster with 100m cell size.

`Maldives` - medium geographic extent.  Produces raster with 100m cell size.

`Canada` - large geographic extent. Demonstrates pushing the limits of raster file size and memory usage.  Produces raster with 400m cell size.

### Run the Simple project

```
cd examples/simple
gen_heatmap config.json
```

## Run the Canada project
You will need to generate random input data first.

```
cd examples/canada

../../scripts/gen_random_shapes config.json canada-poly.geojson

gen_heatmap config.json
```

## Creating a New Project

* Start with copying any of the example folders
* Copy your input shapes in
* Start with a simple config.json. Let it use the default bounds of the input shapes, cell size (100m), etc.

Bounds:
* Useful [tool](https://tools.geofabrik.de/calc/#type=geofabrik_standard&tab=1&proj=EPSG:4326&places=2) to quickly identify bounds.

## Alternative Install (Work in progress)

### Install and run in OSX

Install pipenv to your user home directory:

```
    pip3 install --user pipenv
```

Add user base binary directory to your PATH

```
    /Users/twelch/Library/Python/3.9/bin
```

```
    pip3 install numpy
    pip3 install --no-binary fiona rasterio shapely
```

### Install and run in Windows

* Install VS Code - https://code.visualstudio.com/Download
* Install python 3 from Windows Store if possible, otherwise use python.org.  If you use python.org be sure to 'add Python to my path' and turn off execution aliases for Python (or else it will try to open the windows store every time you run python
* Open terminal and run GitBash terminal

```
    & 'C:\Program Files\Git\bin\bash.exe'
```

Windows Option 1: Docker

Install and start Docker for Windows, then build and start a sapmap Docker image:

```
    git clone https://github.com/seasketch/python-sap-map.git
    cd python-sap-map
    docker-compose build debug # not necessary?
    docker-compose run --rm --service-ports sapmap
```

Windows Option 2: Python virtual environment

```
    pip install virtualenv
    virtualenv env-sapmap
    source env-sapmap/Scripts/activate
    pip install --upgrade pip
```

Follow the rasterio windows instructions - https://rasterio.readthedocs.io/en/latest/installation.html#windows
Pointed to install GDAL and Rasterio wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal.  Look for the latest win_amd64:

```
    pip install .\GDAL-3.3.1-cp39-cp39-win_amd64.whl
    pip install .\rasterio-1.2.6-cp39-cp39-win_amd64.whl
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
```

deactivate the virtual Python environment when done, activate again when needed, or delete

```
    deactivate
```