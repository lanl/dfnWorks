##=====================================================##
## dfnWorks Dockerfile
## dfnworks.lanl.gov
## 
## Copyright (c) 2020. Triad National Security, LLC.
## All rights reserved.
##=====================================================##

# 1. Define && set up the environment
FROM dfn-deps:latest
# MAINTAINER 
ENV APP_PATH=/dfnWorks/
WORKDIR $APP_PATH
# TARGETARCH is set by Docker BuildKit (e.g., amd64, arm64)
ARG TARGETARCH

#ENV https_proxy=
#ENV http_proxy=
#ENV HTTPS_PROXY=
#ENV HTTP_PROXY=

COPY . .
# RUN ["pip3","install","latex"]
# RUN ["pip3","install","datetime"]
# RUN ["pip3","install","rich"]
# RUN ["pip3","install","seaborn"]
# RUN ["python-pip3","install","mplstereonet"]
# RUN ["pip3","install","-U","setuptools"]
# RUN ["apt","install","-y","pipx"]
# RUN ["pipx","install","--include-deps","mplstereonet"]
# RUN ["pip","install","--break-system-packages","mplstereonet"]
# RUN ["pip","install","--break-system-packages","pyvtk"]
# RUN ["pip","install","--break-system-packages","datetime"]
# RUN ["pip","install","--break-system-packages","latex"]
# RUN ["pip","install","--break-system-packages","matplotlib"]

WORKDIR $APP_PATH/pydfnworks/
# RUN ["python3","setup.py","install"]
RUN ["pip","install","--break-system-packages","-r","requirements.txt"]
RUN ["pip","install","--break-system-packages","."]
WORKDIR $APP_PATH

# WORKDIR $APP_PATH/CPP_correct_volumes
# RUN ["make","clean"]
# RUN ["make"]
# RUN ["cp","correct_volume","../bin/correct_volume"]
# WORKDIR $APP_PATH

WORKDIR $APP_PATH/DFNGen
RUN ["make","clean"]
RUN ["make","-j","4"]
RUN ["cp","DFNGen","../bin/DFNGen"]
WORKDIR $APP_PATH

WORKDIR $APP_PATH/DFNTrans
RUN ["make","clean"]
RUN ["make","-j","4"]
RUN ["cp","DFNTrans","../bin/DFNTrans"]
WORKDIR $APP_PATH

WORKDIR $APP_PATH/DFN_Mesh_Connectivity_Test
RUN ["make","clean"]
RUN ["make"]
RUN ["cp","ConnectivityTest","../bin/ConnectivityTest"]

WORKDIR $APP_PATH/lib
RUN ["mkdir","figures"]

WORKDIR $APP_PATH/lib/figures

RUN ["cp","../../pydfnworks/pydfnworks/dfnGen/generation/output_report/figures/dfnWorks.all.black.png","./"]
RUN ["cp","../../pydfnworks/pydfnworks/dfnGen/generation/output_report/figures/lanl-logo-footer.png","./"]

WORKDIR $APP_PATH

RUN ["rm","-Rf","correct_volume/","DFNGen/","DFNTrans/",\
     "DFN_Mesh_Connectivity_Test/","pydfnworks/",".git",".gitignore",\
     "internal/","docker/","scripts/","Dockerfile", "Documentation/", "CPP_correct_volumes"]

# RUN ["apt","install","texlive-latex-extra"]
# Run bash on container launch
CMD ["bash"]
