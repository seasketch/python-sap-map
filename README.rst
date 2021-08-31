
sapmap
======

sapmap is a Python module for generating Spatial Access Priority (SAP) maps from response data.

Install and run in Docker container
-----------------------------------

Install and start Docker, then build and start a sapmap Docker image:
::

    # Clone the sapmap repo locally
    git clone https://github.com/seasketch/python-sap-map.git
    cd python-sap-map
    
    # Start the docker container, attach the source code, and open a shell session inside as root user
    docker-compose run --rm --service-ports sapmap
    
    # Install sapmap module inside container, symlinking to site-packages, making it available to run
    pip install -e ./

    # Run test suite:
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

Install and run in Windows
--------------------------

* Install VS Code - https://code.visualstudio.com/Download
* Install python 3 from Windows Store if possible, otherwise use python.org.  If you use python.org be sure to 'add Python to my path' and turn off execution aliases for Python (or else it will try to open the windows store every time you run python
* Open terminal and run GitBash terminal

::

    & 'C:\Program Files\Git\bin\bash.exe'

Windows Option 1: Docker

Install and start Docker for Windows, then build and start a sapmap Docker image:
::

    git clone https://github.com/seasketch/python-sap-map.git
    cd python-sap-map
    docker-compose build debug # not necessary?
    docker-compose run --rm --service-ports sapmap

Windows Option 2: Python virtual environment
::
    pip install virtualenv
    virtualenv env-sapmap
    source env-sapmap/Scripts/activate
    pip install --upgrade pip

Follow the rasterio windows instructions - https://rasterio.readthedocs.io/en/latest/installation.html#windows
Pointed to install GDAL and Rasterio wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal.  Look for the latest win_amd64:
::

    pip install .\GDAL-3.3.1-cp39-cp39-win_amd64.whl
    pip install .\rasterio-1.2.6-cp39-cp39-win_amd64.whl
    pip install -r requirements.txt
    pip install -r requirements_dev.txt

deactivate the virtual Python environment when done, activate again when needed, or delete
::

    deactivate




