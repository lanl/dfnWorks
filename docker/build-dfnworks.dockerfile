##=====================================================##
## dfnWorks -- application image
## dfnworks.lanl.gov
##
## Copyright (c) 2020. Triad National Security, LLC.
## All rights reserved.
##=====================================================##

ARG DEPS_IMAGE=dfn-deps:latest
FROM ${DEPS_IMAGE}

ENV APP_PATH=/dfnWorks \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1
WORKDIR $APP_PATH

# Copy repo
COPY . .

# Build C++ tools
RUN cd DFNGen && make clean && make && cp DFNGen ../bin/
RUN cd DFNTrans && make clean && make && cp DFNTrans ../bin/
RUN cd DFN_Mesh_Connectivity_Test && make clean && make && cp ConnectivityTest ../bin/

# Install pydfnworks, then clean up source and build artifacts
RUN pip install ./pydfnworks \
 && rm -rf correct_volume/ DFNGen/ DFNTrans/ DFN_Mesh_Connectivity_Test/ \
           pydfnworks/ .git .gitignore internal/ docker/ scripts/ \
           Dockerfile Documentation/ CPP_correct_volumes \
           docs/ dfnWorks.pdf LGPLv3.pdf

CMD ["bash"]
