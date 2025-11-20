##=====================================================##
## dfnWorks Dockerfile
## dfnworks.lanl.gov
## 
## Copyright (c) 2019. Triad National Security, LLC.
## All rights reserved.
##=====================================================##


# 1. Define && set up the environment
FROM ubuntu:latest
# MAINTAINER Daniel Livingston <livingston@lanl.gov>
ENV APP_PATH=/dfnWorks/
WORKDIR $APP_PATH
# TARGETARCH is set by Docker BuildKit (e.g., amd64, arm64)
ARG TARGETARCH

# ENV http_proxy=http://proxyout.lanl.gov:8080
# ENV HTTP_PROXY=http://proxyout.lanl.gov:8080
# ENV https_proxy=http://proxyout.lanl.gov:8080
# ENV HTTPS_PROXY=http://proxyout.lanl.gov:8080

# ENV https_proxy=
# ENV http_proxy=
# ENV HTTPS_PROXY=
# ENV HTTP_PROXY=

RUN ["sed","-i","-e","s|disco|focal|g","/etc/apt/sources.list"]
# 2. Add pre-required packages
# RUN ["apt-get","update","-y"]
# ENV DEBIAN_FRONTEND=noninteractive
# RUN ["apt-get","install","-y","build-essential","python3.12","gfortran","gfortran-12","cmake","git", "wget","libz-dev","m4","bison","texlive-latex-extra"]

# RUN ["apt-get","install","-y","python3-pip","python3-tk","vim","curl","pkg-config","openssh-client"]

# RUN ["apt-get","install","-y","openssh-server","nano","emacs","gcc-12","g++-12", "libcurl4-openssl-dev",\
#         "texlive","texlive-fonts-recommended","dvipng","cm-super","texlive-latex-extra","python3-numpy"] 

ENV DEBIAN_FRONTEND=noninteractive

# update indexes
RUN ["apt-get","update","-y"]

# base tools and headers
RUN ["apt-get","install","-y", \
     "build-essential","cmake","git","wget","curl","pkg-config", \
     "ca-certificates","zlib1g-dev","m4","bison",\
     "libcurl4-openssl-dev",\
     "vim","nano","emacs",\
     "openssh-client","openssh-server"]

# python stack
RUN ["apt-get","install","-y",\
     "python3.12","python3-pip","python3-tk","python3-numpy"]

# fortran and specific compilers
RUN ["apt-get","install","-y",\
     "gfortran","gfortran-12","gcc-12","g++-12"]

# latex and friends
RUN ["apt-get","install","-y",\
     "texlive","texlive-fonts-recommended","texlive-latex-extra","dvipng","cm-super"]

# refresh trust store for tls
RUN ["/usr/sbin/update-ca-certificates"]

# set gcc g++ gfortran default to version 12
RUN ["update-alternatives","--install","/usr/bin/gcc","gcc","/usr/bin/gcc-12","120"]
RUN ["update-alternatives","--install","/usr/bin/g++","g++","/usr/bin/g++-12","120"]
RUN ["update-alternatives","--install","/usr/bin/gfortran","gfortran","/usr/bin/gfortran-12","120"]

# verify versions
RUN ["gcc","--version"]
RUN ["g++","--version"]
RUN ["gfortran","--version"]
RUN ["python3.12","--version"]

# prove the ca bundle exists then test git tls
RUN ["bash","-lc","ls -l /etc/ssl/certs/ca-certificates.crt | cat"]
RUN ["git","config","--system","http.sslCAInfo","/etc/ssl/certs/ca-certificates.crt"]

# clean up apt cache to shrink image
RUN ["bash","-lc","apt-get clean && rm -rf /var/lib/apt/lists/*"]

RUN ["pip","install","--break-system-packages","setuptools"]
RUN ["pip","install","--break-system-packages","numpy"]
RUN ["pip","install","--break-system-packages","h5py"]
RUN ["pip","install","--break-system-packages","matplotlib"]
RUN ["pip","install","--break-system-packages","scipy"]
RUN ["pip","install","--break-system-packages","rich"]
RUN ["pip","install","--break-system-packages","fpdf"]
RUN ["pip","install","--break-system-packages","rich"]
RUN ["pip","install","--break-system-packages","seaborn"]
RUN ["pip","install","--break-system-packages","mpmath"]

RUN ["pip","install","--break-system-packages","mplstereonet"]
RUN ["pip","install","--break-system-packages","pyvtk"]
RUN ["pip","install","--break-system-packages","datetime"]
RUN ["pip","install","--break-system-packages","latex"]
RUN ["pip","install","--break-system-packages","matplotlib"]
RUN ["pip","install","--break-system-packages","datetime"]
RUN ["pip","install","--break-system-packages","latex"]


# RUN ["apt-get","install","-y","python3-setuptools","python3-numpy","python3-h5py",\
# "python3-matplotlib","python3-scipy","python3-networkx",\
# "python3-rich","python3-pyvtk","python3-fpdf","python3-rich","python3-seaborn",\
# "python3-mplstereonet","python3-mpmath", "python3-datetime",\
# "python3-latex"]

# RUN ["pipx","install","setuptools","numpy","h5py","matplotlib","scipy","networkx",\
#     "rich","pyvtk","fpdf","rich","seaborn","mplstereonet","mpmath", "datetime",\
#     "latex"]

# RUN ["pip3","install","-U","setuptools"]

RUN ["mkdir","lib","bin"]

ENV gcc="gcc-10"
ENV g++="g++-10"
ENV gfortran="gfortran-10"
# # ---------------------------------------------------------------------------- #
# # OPTIONAL: Use if you are behind proxy!
# # RUN git config --global url."https://github.com/".insteadOf git@github.com:
# # ---------------------------------------------------------------------------- #

# refresh indexes
# RUN ["apt-get","update","-y"]

# install git and certs
# RUN ["apt-get","install","-y","git","ca-certificates"]

# # refresh the trust store
# RUN ["update-ca-certificates"]
# # if PATH issues ever appear, use the absolute path:
# # RUN ["/usr/sbin/update-ca-certificates"]

# RUN ["/usr/sbin/update-ca-certificates"]

# # prove the bundle exists and is nonempty
# RUN ["bash","-lc","ls -l /etc/ssl/certs/ca-certificates.crt && head -n 3 /etc/ssl/certs/ca-certificates.crt"]

# # belt and suspenders
# ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
# RUN ["git","config","--system","http.sslCAInfo","/etc/ssl/certs/ca-certificates.crt"]

# # verify TLS
# RUN ["git","ls-remote","https://gitlab.com/petsc/petsc.git"]

# # 3.2 Install and configure PETSc
RUN ["git","clone","https://gitlab.com/petsc/petsc","lib/petsc"]
WORKDIR $APP_PATH/lib/petsc
RUN ["git","checkout","v3.24.0"]

ENV PETSC_DIR=/dfnWorks/lib/petsc
ENV PETSC_ARCH=arch-linux2-c-debug

#RUN ./configure --CFLAGS='-O3' --CXXFLAGS='-O3' --FFLAGS='-O3' --with-debugging=no --download-mpich=yes --download-hdf5=yes --download-hdf5-fortran-bindings=yes --download-fblaslapack=yes --download-metis=yes --download-parmetis=yes

# RUN ./configure --with-cc=gcc --with-cxx=g++ --with-fc=gfortran --CFLAGS='-g -O0' --CXXFLAGS='-g -O0' --FFLAGS='-g -O0 -Wno-unused-function -ffree-line-length-none' --with-clanguage=c --with-debug=1 --with-shared-libraries=0 --download-hdf5 --download-hdf5-fortran-bindings --download-metis --download-parmetis --download-fblaslapack --download-mpich=http://www.mpich.org/static/downloads/3.2/mpich-3.2.tar.gz --download-hypre
# RUN ./configure PETSC_ARCH=petsc-arch --CFLAGS='-g -O0' --CXXFLAGS='-g -O0' --FFLAGS='-g -O0 -Wno-unused-function' --with-clanguage=c --with-debug=1 --with-shared-libraries=0 --download-hdf5 --download-metis --download-parmetis --download-fblaslapack --download-hypre

RUN ./configure --with-cc=gcc --with-cxx=g++ --with-fc=gfortran --COPTFLAGS='-O3' --CXXOPTFLAGS='-O3' --FOPTFLAGS='-O3 -Wno-unused-function' --with-debugging=no --download-hdf5=yes --download-hdf5-fortran-bindings=yes --download-fblaslapack=yes --download-metis=yes --download-parmetis=yes --download-mpich=yes

RUN make PETSC_DIR=/dfnWorks/lib/petsc PETSC_ARCH=arch-linux2-c-debug all

#
WORKDIR $APP_PATH

# # 3.3 Install and configure PFLOTRAN
RUN git clone https://bitbucket.org/pflotran/pflotran
WORKDIR $APP_PATH/pflotran/src/pflotran

RUN make pflotran
WORKDIR $APP_PATH
RUN ["mv","pflotran/src/pflotran/pflotran","bin/pflotran"]
RUN ["rm","-Rf","pflotran/"]

WORKDIR $APP_PATH

# # # # 3.0 Install FEHM
RUN ["rm","-Rf","FEHM/"]
RUN ["git","clone","https://github.com/hymanjd/FEHM.git","FEHM"]
WORKDIR $APP_PATH/FEHM/src
RUN ["make","-f","Makefile"]
WORKDIR $APP_PATH
RUN ["mv","FEHM/src/xfehm","bin/fehm"]
RUN ["rm","-Rf","FEHM/"]
WORKDIR $APP_PATH

# # # 3.1 Install and configure LaGriT
ENV RSYNC_PROXY=http://proxyout.lanl.gov:8080
RUN ["rm","-Rf","LaGriT/"] 
RUN ["git","clone","https://github.com/hymanjd/LaGriT.git"]
WORKDIR $APP_PATH/LaGriT
# RUN ./install-exodus.sh
WORKDIR $APP_PATH/LaGriT
RUN ["mkdir","build"]
WORKDIR $APP_PATH/LaGriT/build
RUN ["cmake",".."]
#RUN ["cmake","..", "-DLAGRIT_BUILD_EXODUS=ON"]
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
