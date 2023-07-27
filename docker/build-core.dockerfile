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

#ENV https_proxy=http://proxyout.lanl.gov:8080
#ENV http_proxy=http_proxy=http://proxyout.lanl.gov:8080
#ENV HTTPS_PROXY=http_proxy=http://proxyout.lanl.gov:8080
#ENV HTTP_PROXY=http_proxy=http://proxyout.lanl.gov:8080
ENV https_proxy=
ENV http_proxy=
ENV HTTPS_PROXY=
ENV HTTP_PROXY=

RUN ["sed","-i","-e","s|disco|focal|g","/etc/apt/sources.list"]
# 2. Add pre-required packages
RUN ["apt-get","update","-y"]
ENV DEBIAN_FRONTEND=noninteractive
RUN ["apt-get","install","-y","build-essential","gfortran","gfortran-10","cmake","git",\
        "wget","libz-dev","m4","bison","python3",\
        "python3-pip","python3-tk","vim","curl","pkg-config","openssh-client",\
        "openssh-server","valgrind","nano","emacs","gcc-10","g++-10"]

RUN ["pip3","install","setuptools","numpy","h5py","matplotlib","scipy","networkx",\
    "rich","pyvtk","fpdf","rich","seaborn","mplstereonet","mpmath"]

RUN ["pip3","install","-U","setuptools"]

RUN ["mkdir","lib","bin"]

ENV alias gcc="gcc-10"
ENV alias g++="g++-10"
ENV alias gfortran="gfortran-10"
# # ---------------------------------------------------------------------------- #
# # OPTIONAL: Use if you are behind proxy!
# # RUN git config --global url."https://github.com/".insteadOf git@github.com:
# # ---------------------------------------------------------------------------- #

# # 3.2 Install and configure PETSc
RUN ["git","clone","https://gitlab.com/petsc/petsc.git","lib/petsc"]
WORKDIR $APP_PATH/lib/petsc
RUN ["git","checkout","v3.19.3"]

ENV PETSC_DIR=/dfnWorks/lib/petsc
ENV PETSC_ARCH=arch-linux2-c-debug

RUN ./configure --CFLAGS='-O3' --CXXFLAGS='-O3' --FFLAGS='-O3' --with-debugging=no --download-mpich=yes --download-hdf5=yes --download-hdf5-fortran-bindings=yes --download-fblaslapack=yes --download-metis=yes --download-parmetis=yes

#RUN ./configure PETSC_ARCH=petsc-arch --with-cc=gcc --with-cxx=g++ --with-fc=gfortran --CFLAGS='-g -O0' --CXXFLAGS='-g -O0' --FFLAGS='-g -O0 -Wno-unused-function' --with-clanguage=c --with-debug=1 --with-shared-libraries=0 --download-hdf5 --download-metis --download-parmetis --download-fblaslapack --download-mpich=http://www.mpich.org/static/downloads/3.2/mpich-3.2.tar.gz --download-hypre
# RUN ./configure PETSC_ARCH=petsc-arch --CFLAGS='-g -O0' --CXXFLAGS='-g -O0' --FFLAGS='-g -O0 -Wno-unused-function' --with-clanguage=c --with-debug=1 --with-shared-libraries=0 --download-hdf5 --download-metis --download-parmetis --download-fblaslapack --download-hypre

RUN make

WORKDIR $APP_PATH

# # 3.3 Install and configure PFLOTRAN
# RUN ["git","clone","--depth","1","https://bitbucket.org/pflotran/pflotran"]
RUN ["git","clone","--depth","1","https://bitbucket.org/pflotran/pflotran"]
WORKDIR $APP_PATH/pflotran/src/pflotran
RUN ["git","fetch"]
RUN ["git", "branch"]

# RUN ["git","checkout","maint/v4.0"]
RUN ["make","pflotran"]
WORKDIR $APP_PATH
RUN ["mv","pflotran/src/pflotran/pflotran","bin/pflotran"]
RUN ["rm","-Rf","pflotran/"]

WORKDIR $APP_PATH

# # # # 3.0 Install FEHM
RUN ["git","clone","--depth","1","https://github.com/lanl/FEHM.git","FEHM"]
WORKDIR $APP_PATH/FEHM/src
RUN ["make","-f","Makefile"]
WORKDIR $APP_PATH
RUN ["mv","FEHM/src/xfehm_v3.3.1","bin/fehm"]
RUN ["rm","-Rf","FEHM/"]

WORKDIR $APP_PATH

# # # 3.1 Install and configure LaGriT
RUN ["git","clone","https://github.com/lanl/LaGriT.git"]
WORKDIR $APP_PATH/LaGriT
RUN ["git","fetch","--all"]
RUN ["git","branch"]
RUN ["git","checkout","jdhdev"]

RUN ["mkdir","build"]
WORKDIR $APP_PATH/LaGriT/build
RUN ["cmake",".."]
RUN ["make"]
WORKDIR $APP_PATH
RUN ["mv","LaGriT/build/lagrit","bin/lagrit"]
RUN ["rm","-Rf","LaGriT/"]

WORKDIR $APP_PATH

RUN ["update-alternatives","--install","/usr/bin/python","python","/usr/bin/python3","10"]

# 4. Configure paths for dfnWorks in JSON format
RUN echo { >> ~/.dfnworksrc
RUN echo \"dfnworks_PATH\": \"$APP_PATH\", >> ~/.dfnworksrc
RUN echo \"PETSC_DIR\": \"/dfnWorks/lib/petsc\", >> ~/.dfnworksrc
RUN echo \"PETSC_ARCH\": \"arch-linux2-c-debug\", >> ~/.dfnworksrc
RUN echo \"PFLOTRAN_EXE\": \"$APP_PATH/bin/pflotran\", >> ~/.dfnworksrc
RUN echo \"PYTHON_EXE\": \"/usr/bin/python3\", >> ~/.dfnworksrc
RUN echo \"LAGRIT_EXE\": \"$APP_PATH/bin/lagrit\", >> ~/.dfnworksrc
RUN echo \"FEHM_EXE\": \"$APP_PATH/bin/fehm\" >> ~/.dfnworksrc
RUN echo } >> ~/.dfnworksrc

# 4.1 Set bashrc and vimrc
RUN echo alias lt=\'ls -ltrh\' >> ~/.bashrc
RUN echo alias ..=\'cd ..\' >> ~/.bashrc
RUN echo export PATH=$PATH:$APP_PATH/bin >> ~/.bashrc

RUN echo syntax on >> ~/.vimrc
RUN echo set number >> ~/.vimrc
RUN echo filetype plugin indent on >> ~/.vimrc
RUN echo set tabstop=4 >> ~/.vimrc
RUN echo set shiftwidth=4 >> ~/.vimrc
RUN echo set expandtab >> ~/.vimrc

# # # Run bash on container launch
CMD ["bash"]
