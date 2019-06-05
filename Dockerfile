##=====================================================##
## dfnWorks Dockerfile
## dfnworks.lanl.gov
## 
## Copyright (c) 2019. Triad National Security, LLC.
## All rights reserved.
##=====================================================##

# 1. Define && set up the environment
FROM ubuntu:latest
MAINTAINER Daniel Livingston <livingston@lanl.gov>
ENV APP_PATH=/dfnWorks/
WORKDIR $APP_PATH
COPY . .
RUN ["apt-get","update","-y"]

# 2. Add pre-required packages
ENV DEBIAN_FRONTEND=noninteractive
RUN ["apt-get","install","-y","build-essential","gfortran","cmake","git","python","python-pip"]
RUN ["apt-get","install","-y","wget","libz-dev","m4","bison","python3","python3-pip","python3-tk","vim","curl"]
RUN ["apt-get","install","-y","pkg-config","openssh-client","openssh-server","valgrind"]

RUN ["pip3","install","setuptools","numpy","h5py","matplotlib","scipy","networkx"]

# ---------------------------------------------------------------------------- #
# OPTIONAL: Use if you are behind proxy!
RUN git config --global url."https://github.com/".insteadOf git@github.com:
# ---------------------------------------------------------------------------- #

# 3.0 Install FEHM
RUN ["git","clone","--depth","1","https://github.com/lanl/FEHM.git","FEHM"]
WORKDIR $APP_PATH/FEHM/src
RUN ["make","-f","Makefile"]
WORKDIR $APP_PATH

# 3.1 Install and configure LaGriT
RUN ["git","clone","--depth","1","https://github.com/lanl/LaGriT.git"]
WORKDIR $APP_PATH/LaGriT
RUN ["make","exodus"]
RUN ["make","release"]
WORKDIR $APP_PATH

# 3.2 Install and configure PETSc
RUN ["git","clone","https://bitbucket.org/petsc/petsc","petsc"]
WORKDIR $APP_PATH/petsc
RUN ["git","checkout","v3.10.2"]

ENV PETSC_DIR=$APP_PATH/petsc
ENV PETSC_ARCH=arch-linux2-c-debug

RUN ["./configure","--CFLAGS=-O3","--CXXFLAGS=-O3","--FFLAGS=-O3","--with-debugging=no","--download-mpich=yes","--download-hdf5=yes","--download-fblaslapack=yes","--download-metis=yes","--download-parmetis=yes"]
WORKDIR $PETSC_DIR
RUN ["make","all"]
WORKDIR $APP_PATH

# 3.3 Install and configure PFLOTRAN
RUN ["git","clone","--depth","1","https://bitbucket.org/pflotran/pflotran"]
WORKDIR $APP_PATH/pflotran/src/pflotran
RUN ["make","pflotran"]
WORKDIR $APP_PATH

# 4. Configure paths for dfnWorks in JSON format
RUN echo { >> ~/.dfnworksrc
RUN echo \"dfnworks_PATH\": \"$APP_PATH\", >> ~/.dfnworksrc
RUN echo \"PETSC_DIR\": \"$APP_PATH/petsc\", >> ~/.dfnworksrc
RUN echo \"PETSC_ARCH\": \"arch-linux2-c-debug\", >> ~/.dfnworksrc
RUN echo \"PFLOTRAN_EXE\": \"$APP_PATH/pflotran/src/pflotran/pflotran\", >> ~/.dfnworksrc
RUN echo \"PYTHON_EXE\": \"/usr/bin/python3\", >> ~/.dfnworksrc
RUN echo \"LAGRIT_EXE\": \"$APP_PATH/LaGriT/src/lagrit\", >> ~/.dfnworksrc
RUN echo \"FEHM_EXE\": \"$APP_PATH/FEHM/src/xfehm_v3.3.1\" >> ~/.dfnworksrc
RUN echo } >> ~/.dfnworksrc

# 5. Begin dfnWorks setup
# Override default Python and pip to 3.x versions
RUN ["update-alternatives","--install","/usr/bin/python","python","/usr/bin/python3","10"]
#update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

WORKDIR $APP_PATH/pydfnworks/
RUN ["python3","setup.py","install"]
WORKDIR $APP_PATH

# Run bash on container launch
CMD ["bash"]


