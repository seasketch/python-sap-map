# ------ Base image

FROM perrygeo/gdal-base:latest as base

RUN mkdir /work/
WORKDIR /work/

COPY requirements.txt /work/requirements.txt
COPY requirements_dev.txt /work/requirements_dev.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python -m pip install cython numpy -c requirements.txt
RUN python -m pip install --no-binary fiona,rasterio,shapely -r requirements.txt
RUN pip uninstall cython --yes

# ------ Workspace image - for local use

FROM base as workspace
RUN pip install -r requirements_dev.txt
RUN echo "export PATH=/work/scripts:${PATH}" >> /root/.bashrc
WORKDIR /work

# ------ Production image

FROM python:3.9.6-slim-buster as production

# Install the previously-built shared libaries from the base image
COPY --from=base /usr/local /usr/local
RUN ldconfig