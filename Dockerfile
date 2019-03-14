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
#    TESTING: rm curl and everything after
ENV DEBIAN_FRONTEND=noninteractive
RUN ["apt-get","install","-y","build-essential","gfortran","cmake","git","wget","libz-dev","m4","bison","python","python-pip","python-tk","curl","pkg-config","openssh-client","openssh-server"]
RUN ["pip","install","-U","pip","setuptools"]
RUN ["pip","install","numpy","h5py","matplotlib","scipy"]

RUN ["which","python"]

# ---------------------------------------------------------------------------- #
# OPTIONAL: Use if you are behind proxy!
RUN git config --global url."https://github.com/".insteadOf git@github.com:
# ---------------------------------------------------------------------------- #


ENV DFNHOME=$APP_PATH

# 3.1 Install and configure LaGriT
RUN ["git","clone","https://github.com/lanl/LaGriT.git"]
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
RUN ["git","clone","https://bitbucket.org/pflotran/pflotran"]
WORKDIR $APP_PATH/pflotran/src/pflotran
RUN ["make","pflotran"]
WORKDIR $APP_PATH

# 4. Begin dfnWorks setup
RUN ["ls","-al","/dfnWorks/"]

ENV dfnWorks_PATH=$APP_PATH
ENV PFLOTRAN_DIR=$APP_PATH/pflotran
#ENV python_dfn=NONE
ENV lagrit_dfn=$APP_PATH/LaGriT/src/lagrit

WORKDIR $APP_PATH/pydfnworks/bin/
RUN ["python","fix_paths.py"]
WORKDIR $APP_PATH/pydfnworks/
RUN ["python","setup.py","install"]
WORKDIR $APP_PATH

# 5. Run dfnWorks test
WORKDIR $APP_PATH/pydfnworks/bin/
#RUN ["python","run.py","-name","${APP_PATH}/4_user_defined_rectangles","-input","${APP_PATH}/tests/4_user_defined_rectangles.txt","-ncpu","4"]

# Run (something??) on container launch
CMD ["python"]


