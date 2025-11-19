##=====================================================##
## LaGrit Dockerfile
## lagrit.lanl.gov
##
## Copyright (c) 2019. Triad National Security, LLC.
## All rights reserved.
##=====================================================##


# 1. Define && set up the environment
FROM ubuntu:latest
MAINTAINER Daniel Livingston <livingston@lanl.gov>
ENV APP_PATH=/lagrit/
WORKDIR $APP_PATH
# TARGETARCH is set by Docker BuildKit (e.g., amd64, arm64)
ARG TARGETARCH

ENV http_proxy=http://proxyout.lanl.gov:8080
ENV HTTP_PROXY=http://proxyout.lanl.gov:8080
ENV https_proxy=http://proxyout.lanl.gov:8080
ENV HTTPS_PROXY=http://proxyout.lanl.gov:8080

#ENV https_proxy=
#ENV http_proxy=
#ENV HTTPS_PROXY=
#ENV HTTP_PROXY=

# 2. Add pre-required packages
RUN ["apt-get","update","-y"]
ENV DEBIAN_FRONTEND=noninteractive
RUN ["apt-get","install","-y","build-essential","gfortran","gfortran-10","cmake","git",\
        "wget","libz-dev","m4","bison","python3",\
        "python3-pip","python3-tk","vim","curl","pkg-config","openssh-client",\
        "openssh-server","valgrind","nano","emacs","gcc-10","g++-10", "libcurl4-openssl-dev"]

RUN ["pip3","install","setuptools","numpy","h5py","matplotlib","scipy","networkx",\
    "rich","pyvtk","fpdf","rich","seaborn","mplstereonet","mpmath"]

RUN ["pip3","install","-U","setuptools"]

RUN ["mkdir","lib","bin"]

WORKDIR $APP_PATH

# # # 3.1 Install and configure LaGriT
RUN ["git","clone","--depth","1","https://github.com/lanl/LaGriT.git"]
WORKDIR $APP_PATH/LaGriT
RUN ./install-exodus.sh
# RUN ["git","fetch","--all"]
# RUN ["git","branch"]
# RUN ["git","checkout","jdhdev"]

RUN ["mkdir","build"]
WORKDIR $APP_PATH/LaGriT/build
RUN ["cmake","..","-DLAGRIT_BUILD_EXODUS=ON"]
RUN ["make"]
WORKDIR $APP_PATH
RUN ["mv","LaGriT/build/lagrit","bin/lagrit"]
RUN ["rm","-Rf","LaGriT/"]

# WORKDIR $APP_PATH

# RUN ["update-alternatives","--install","/usr/bin/python","python","/usr/bin/python3","10"]

# # # Run bash on container launch
CMD ["bash"]
