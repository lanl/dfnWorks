##=====================================================##
## dfnWorks Dockerfile
## dfnworks.lanl.gov
## 
## Copyright (c) 2020. Triad National Security, LLC.
## All rights reserved.
##=====================================================##

# 1. Define && set up the environment
FROM dfn-deps:latest
MAINTAINER Daniel Livingston <livingston@lanl.gov>
ENV APP_PATH=/dfnWorks/
WORKDIR $APP_PATH

ENV https_proxy=
ENV http_proxy=
ENV HTTPS_PROXY=
ENV HTTP_PROXY=

COPY . .

# RUN ["pip3","install","matplotlib"]
# RUN ["pip3","install","fpdf"]
# RUN ["pip3","install","rich"]
# RUN ["pip3","install","seaborn"]
# RUN ["pip3","install","mplstereonet"]
# RUN ["pip3","install","-U","setuptools"]


WORKDIR $APP_PATH/pydfnworks/
RUN ["python3","setup.py","install"]
WORKDIR $APP_PATH

WORKDIR $APP_PATH/C_stor_correct
RUN ["make","clean"]
RUN ["make"]
RUN ["cp","correct_stor","../bin/correct_stor"]
WORKDIR $APP_PATH

WORKDIR $APP_PATH/C_uge_correct
RUN ["make","clean"]
RUN ["make"]
RUN ["cp","correct_uge","../bin/correct_uge"]
WORKDIR $APP_PATH

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

RUN ["rm","-Rf","C_stor_correct/","C_uge_correct/","DFNGen/","DFNTrans/",\
     "DFN_Mesh_Connectivity_Test/","pydfnworks/",".git",".gitignore",\
     "internal/","docker/","scripts/","Dockerfile", "Documentation/"]

# Run bash on container launch
CMD ["bash"]
