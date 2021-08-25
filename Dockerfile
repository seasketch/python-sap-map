# ------ Base image

FROM perrygeo/gdal-base:latest as base

RUN mkdir /work/
WORKDIR /work/

COPY requirements.txt /work/requirements.txt
RUN pip install -r requirements.txt

RUN python -m pip install cython numpy -c requirements.txt
RUN python -m pip install --no-binary fiona,rasterio,shapely -r requirements.txt
RUN pip uninstall cython --yes

# ------ Workspace image - for local use

FROM base as workspace
RUN pip install -r requirements_dev.txt
WORKDIR /work

# ------ Production image

FROM python:3.8-slim-buster as production

# Install the previously-built shared libaries from the base image
COPY --from=base /usr/local /usr/local
RUN ldconfig