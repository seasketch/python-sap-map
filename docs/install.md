# Installation and Usage

A Docker recipe is available to install `sapmap` in an isolated virtual environment on your local computer with all dependencies.  In the future, a published module may be made available.

1. First install and start [Docker Desktop](https://www.docker.com/) on your local computer.  Windows, MacOS, Linux are all supported.

2. Clone the code, build a docker image, run a container with the image and open a shell to it, run final sap setup, then run the test suite to verify it's working:
```bash
    git clone https://github.com/seasketch/python-sap-map.git
    cd python-sap-map
    docker-compose build sapmap
    docker-compose run --rm --service-ports sapmap
    setup_sap_map
    pytest
```

## Example Projects

Multiple example projects are included that can be run out of the box.

[Simple](/examples/simple) - small geographic extent.  Very simple test dataset with polygons that aligned to 100m boundaries for ease of interpreting the result.  Produces raster with 100m cell size.

[Maldives](/examples/maldives) - medium geographic extent.  Produces raster with 100m cell size.

[Canada](/examples/canada) - large geographic extent. Demonstrates pushing the limits of raster file size and memory usage.  Produces raster with 400m cell size.

### Run the Simple project

```
cd examples/simple
gen_sap_map config.json
```

## Run the Canada project
You will need to generate random input data first.

```
cd examples/canada

../../scripts/gen_random_shapes config.json canada-poly.geojson

gen_sap_map config.json
```

## Creating a New Project

* Start with copying any of the example folders
* Copy your input shapes in
* Start with a simple config.json. Let it use the default bounds of the input shapes, cell size (100m), etc.

Bounds:
* Useful [tool](https://tools.geofabrik.de/calc/#type=geofabrik_standard&tab=1&proj=EPSG:4326&places=2) to quickly identify bounds.