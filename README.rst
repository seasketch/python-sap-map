
sapmap
======

sapmap is a Python module for generating Spatial Access Priority (SAP) maps from response data.

Install and run in Docker container
-----------------------------------

Install and start Docker, then build and start a sapmap Docker image:
::

    git clone https://github.com/seasketch/heatmap.git
    cd heatmap
    docker-compose build debug # not necessary?
    docker-compose run --rm --service-ports sapmap

Run test suite:
::

    pytest


Debug using VSCode from within container:
::

    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client examples/simple_sap_map.py

In VSCode, set a breakpoint, Click `Debug` in the left menu, then click `Python Attach` to attach to the waiting process and start it running.

Install and run in OSX
----------------------

Install pipenv to your user home directory:
::

    pip3 install --user pipenv

Add user base binary directory to your PATH
::

    /Users/twelch/Library/Python/3.9/bin

::

    pip3 install numpy
    pip3 install --no-binary fiona rasterio shapely


