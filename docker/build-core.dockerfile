# syntax=docker/dockerfile:1
##=====================================================##
## dfnWorks -- core / dependency image (build ONCE)
## dfnworks.lanl.gov
##
## Copyright (c) 2019. Triad National Security, LLC.
## All rights reserved.
##
## This image is heavy and slow to build (PETSc/PFLOTRAN/FEHM/LaGriT are
## compiled from source). Build it once per arch, push as a multi-arch
## manifest, then iterate on the thin pydfnworks image on top of it.
##=====================================================##

# Pin a concrete Ubuntu release for reproducible, multi-arch builds.
# 24.04 (noble) ships gcc/g++/gfortran-12 for BOTH amd64 and arm64.
FROM ubuntu:24.04

LABEL org.opencontainers.image.title="dfn-deps" \
      org.opencontainers.image.description="dfnWorks core deps: PETSc, PFLOTRAN, FEHM, LaGriT + Python stack" \
      org.opencontainers.image.url="https://dfnworks.lanl.gov" \
      org.opencontainers.image.vendor="Triad National Security, LLC"

# Provided automatically by buildx for each target platform (amd64, arm64...).
ARG TARGETARCH
ARG TARGETPLATFORM

ENV APP_PATH=/dfnWorks \
    DEBIAN_FRONTEND=noninteractive \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

WORKDIR $APP_PATH

RUN echo "Building dfn-deps for: ${TARGETPLATFORM} (arch=${TARGETARCH})"

# --- OS packages -----------------------------------------------------------
# Single layer; clean apt lists in the SAME layer so they don't bloat history.
# NOTE: no --no-install-recommends here on purpose -- the texlive metapackages
# rely on recommends for fonts that matplotlib's LaTeX rendering needs.
RUN apt-get update -y && apt-get install -y \
      build-essential cmake git wget curl pkg-config ca-certificates \
      zlib1g-dev m4 bison libcurl4-openssl-dev \
      python3 python3-pip python3-tk python3-dev \
      gfortran gfortran-12 gcc-12 g++-12 \
      texlive texlive-fonts-recommended texlive-latex-extra dvipng cm-super \
      vim nano openssh-client \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Pin gcc/g++/gfortran to v12 (works on amd64 and arm64). PETSc + the Fortran
# codes are happiest on 12; newer gfortran tightens argument checking.
RUN for t in gcc g++ gfortran; do \
      update-alternatives --install /usr/bin/$t $t /usr/bin/$t-12 120; \
    done

# Make `python` -> python3 available too.
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# Sanity check toolchain (shows in build logs per-arch).
RUN gcc --version && g++ --version && gfortran --version && python3 --version

# git over TLS using the system CA bundle.
RUN git config --system http.sslCAInfo /etc/ssl/certs/ca-certificates.crt

# --- Python stack ----------------------------------------------------------
# Pre-install the common heavy wheels so the app image's
# `pip install -r requirements.txt` is mostly cache hits.
# (pydfnworks/requirements.txt remains the source of truth at app-build time.)
RUN python3 -m pip install \
      setuptools numpy h5py scipy matplotlib seaborn networkx \
      rich fpdf mpmath mplstereonet pyvtk \
      datetime latex

RUN mkdir -p lib bin
ENV PATH=$APP_PATH/bin:$PATH

# ---------------------------------------------------------------------------
# 3.2 PETSc
# ---------------------------------------------------------------------------
# PETSC_ARCH renamed to reflect that this is an OPTIMIZED (non-debug) build.
# It is written into ~/.dfnworksrc below so pydfnworks finds it at runtime.
ENV PETSC_DIR=$APP_PATH/lib/petsc \
    PETSC_ARCH=arch-linux-c-opt

# PETSc version pinned to the one PFLOTRAN v6.0 lists as "supported"
# (per documentation.pflotran.org -> Linux install). Bump this in lockstep
# with PFLOTRAN's supported-version note when you update.
RUN git clone --depth 1 --branch v3.24.5 https://gitlab.com/petsc/petsc lib/petsc
WORKDIR $PETSC_DIR
RUN ./configure \
      --with-cc=gcc --with-cxx=g++ --with-fc=gfortran \
      --COPTFLAGS=-O3 --CXXOPTFLAGS=-O3 --FOPTFLAGS='-O3 -Wno-unused-function' \
      --with-debugging=no \
      --download-mpich=yes \
      --download-hdf5=yes --download-hdf5-fortran-bindings=yes \
      --download-fblaslapack=yes \
      --download-metis=yes --download-parmetis=yes
RUN make PETSC_DIR=$PETSC_DIR PETSC_ARCH=$PETSC_ARCH all

WORKDIR $APP_PATH

# ---------------------------------------------------------------------------
# 3.3 PFLOTRAN
# ---------------------------------------------------------------------------
# PFLOTRAN is built from its default branch, matching the official Linux
# install docs. With PETSc pinned to the supported v3.24.5 above, this branch
# is the combination PFLOTRAN v6.0 is tested against.
RUN git clone --depth 1 https://bitbucket.org/pflotran/pflotran \
 && make -C pflotran/src/pflotran pflotran \
 && mv pflotran/src/pflotran/pflotran bin/pflotran \
 && rm -rf pflotran

# ---------------------------------------------------------------------------
# 3.0 FEHM
# ---------------------------------------------------------------------------
RUN git clone --depth 1 https://github.com/hymanjd/FEHM.git FEHM \
 && make -C FEHM/src -f Makefile \
 && mv FEHM/src/xfehm bin/fehm \
 && rm -rf FEHM

# ---------------------------------------------------------------------------
# 3.1 LaGriT  (ExodusII left OFF, matching the original build)
# ---------------------------------------------------------------------------
RUN git clone --depth 1 https://github.com/hymanjd/LaGriT.git \
 && cmake -S LaGriT -B LaGriT/build \
 && make -C LaGriT/build -j"$(nproc)" \
 && mv LaGriT/build/lagrit bin/lagrit \
 && rm -rf LaGriT

WORKDIR $APP_PATH

# ---------------------------------------------------------------------------
# 4. dfnWorks runtime config (written once, single layer)
# ---------------------------------------------------------------------------
RUN cat > /root/.dfnworksrc <<EOF
{
  "dfnworks_PATH": "${APP_PATH}/",
  "PETSC_DIR": "${PETSC_DIR}",
  "PETSC_ARCH": "${PETSC_ARCH}",
  "PFLOTRAN_EXE": "${APP_PATH}/bin/pflotran",
  "PYTHON_EXE": "/usr/bin/python3",
  "LAGRIT_EXE": "${APP_PATH}/bin/lagrit",
  "FEHM_EXE": "${APP_PATH}/bin/fehm"
}
EOF

# 4.1 Shell niceties
RUN cat >> /root/.bashrc <<EOF
alias lt='ls -ltrh'
alias ..='cd ..'
export PATH=\$PATH:${APP_PATH}/bin
EOF

RUN cat > /root/.vimrc <<'EOF'
syntax on
set number
filetype plugin indent on
set tabstop=4
set shiftwidth=4
set expandtab
EOF

CMD ["bash"]
