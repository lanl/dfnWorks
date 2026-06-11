##=====================================================##
## dfnWorks -- core dependency image (build once)
## dfnworks.lanl.gov
##
## Copyright (c) 2019. Triad National Security, LLC.
## All rights reserved.
##=====================================================##

# ubuntu:24.04 ships gcc/g++/gfortran-12 for both amd64 and arm64.
FROM ubuntu:24.04

ENV APP_PATH=/dfnWorks \
    DEBIAN_FRONTEND=noninteractive \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PETSC_DIR=/dfnWorks/lib/petsc \
    PETSC_ARCH=arch-linux-c-opt

WORKDIR $APP_PATH
RUN mkdir -p lib bin
ENV PATH=$APP_PATH/bin:$PATH

# OS packages
RUN apt-get update -y && apt-get install -y \
      build-essential cmake git wget curl pkg-config ca-certificates \
      zlib1g-dev m4 bison libcurl4-openssl-dev \
      python3 python3-pip python3-tk python3-dev \
      gfortran gfortran-12 gcc-12 g++-12 \
      texlive texlive-fonts-recommended texlive-latex-extra dvipng cm-super \
      vim nano openssh-client \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Pin to gcc/g++/gfortran-12 (consistent on amd64 and arm64)
RUN update-alternatives --install /usr/bin/gcc      gcc      /usr/bin/gcc-12      120 \
 && update-alternatives --install /usr/bin/g++      g++      /usr/bin/g++-12      120 \
 && update-alternatives --install /usr/bin/gfortran gfortran /usr/bin/gfortran-12 120 \
 && update-alternatives --install /usr/bin/python   python   /usr/bin/python3     10

# Python packages
RUN python3 -m pip install \
      setuptools numpy h5py scipy matplotlib seaborn networkx \
      rich fpdf mpmath mplstereonet pyvtk datetime latex

# PETSc -- must remain in the image; PFLOTRAN links against it.
# Pinned to v3.24.5, the version PFLOTRAN v6.0 lists as supported.
# https://documentation.pflotran.org/user_guide/how_to/installation/linux.html
RUN git clone --depth 1 --branch v3.24.5 https://gitlab.com/petsc/petsc lib/petsc
RUN cd lib/petsc && ./configure \
      --with-cc=gcc --with-cxx=g++ --with-fc=gfortran \
      --COPTFLAGS=-O3 --CXXOPTFLAGS=-O3 --FOPTFLAGS='-O3 -Wno-unused-function' \
      --with-debugging=no \
      --download-mpich=yes \
      --download-hdf5=yes --download-hdf5-fortran-bindings=yes \
      --download-fblaslapack=yes \
      --download-metis=yes --download-parmetis=yes
RUN cd lib/petsc && make PETSC_DIR=$PETSC_DIR PETSC_ARCH=$PETSC_ARCH all

# PFLOTRAN
RUN git clone --depth 1 https://bitbucket.org/pflotran/pflotran \
 && make -C pflotran/src/pflotran pflotran \
 && mv pflotran/src/pflotran/pflotran bin/pflotran \
 && rm -rf pflotran

# FEHM
RUN git clone --depth 1 https://github.com/hymanjd/FEHM.git FEHM \
 && make -C FEHM/src -f Makefile \
 && mv FEHM/src/xfehm bin/fehm \
 && rm -rf FEHM

# LaGriT
RUN git clone --depth 1 https://github.com/hymanjd/LaGriT.git \
 && cmake -S LaGriT -B LaGriT/build \
 && make -C LaGriT/build -j"$(nproc)" \
 && mv LaGriT/build/lagrit bin/lagrit \
 && rm -rf LaGriT

# Runtime config
RUN printf '{\n  "dfnworks_PATH": "/dfnWorks/",\n  "PETSC_DIR": "/dfnWorks/lib/petsc",\n  "PETSC_ARCH": "arch-linux-c-opt",\n  "PFLOTRAN_EXE": "/dfnWorks/bin/pflotran",\n  "PYTHON_EXE": "/usr/bin/python3",\n  "LAGRIT_EXE": "/dfnWorks/bin/lagrit",\n  "FEHM_EXE": "/dfnWorks/bin/fehm"\n}\n' > /root/.dfnworksrc

RUN printf 'alias lt="ls -ltrh"\nalias ..="cd .."\nexport PATH=$PATH:/dfnWorks/bin\n' >> /root/.bashrc

RUN printf 'syntax on\nset number\nfiletype plugin indent on\nset tabstop=4\nset shiftwidth=4\nset expandtab\n' > /root/.vimrc

CMD ["bash"]
