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

# replace shell with bash so we can source files
# RUN rm /bin/sh && ln -s /bin/bash /bin/shapely

# update the repository sources list
# and install dependencies
RUN apt-get --allow-releaseinfo-change update
RUN apt-get update \
    && apt-get install -y curl \
    && apt-get -y autoclean

RUN pip install -r requirements_dev.txt
RUN pip install -r docs/requirements.txt
# RUN apt-get --allow-releaseinfo-change update
# RUN apt -y install nodejs
# RUN apt -y install npm

#Install nodejs and npm
# RUN mkdir /usr/local/nvm
# ENV NVM_DIR /usr/local/nvm
# ENV NODE_VERSION 14
# ENV NVM_INSTALL_PATH $NVM_DIR/versions/node/v$NODE_VERSION
# RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
# RUN source $NVM_DIR/nvm.sh \
#    && nvm install $NODE_VERSION \
#    && nvm alias default $NODE_VERSION \
#    && nvm use default
# ENV NODE_PATH $NVM_INSTALL_PATH/lib/node_modules
# ENV PATH $NVM_INSTALL_PATH/bin:$PATH
# RUN npm -v
# RUN node -v
# RUN source ~/.bashrc && nvm --version
# RUN nvm -v

RUN echo "export PATH=/work/scripts:${PATH}" >> /root/.bashrc
WORKDIR /work

# ------ Production image

FROM python:3.9.6-slim-buster as production

# Install the previously-built shared libaries from the base image
COPY --from=base /usr/local /usr/local
RUN ldconfig