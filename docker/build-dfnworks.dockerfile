# syntax=docker/dockerfile:1
##=====================================================##
## dfnWorks -- application image (pydfnworks + DFN C++ tools)
## dfnworks.lanl.gov
##
## Copyright (c) 2020. Triad National Security, LLC.
## All rights reserved.
##
## Builds FROM the heavy core image. Multi-stage so the C++ source trees and
## .git never land in the final image, and layer-ordered so a pure pydfnworks
## change only rebuilds the last pip layer ("update on the fly").
##
## Build context = the dfnWorks repo root (must contain DFNGen/, DFNTrans/,
## DFN_Mesh_Connectivity_Test/, pydfnworks/).
##=====================================================##

# Point this at YOUR core image. Pin a real tag (e.g. dfn-deps:2025-06) once
# stable, instead of :latest, for reproducible builds.
ARG DEPS_IMAGE=ees16/dfn-deps:latest

# ===========================================================================
# Stage 1 -- compile the C++ DFN tools
# ===========================================================================
FROM ${DEPS_IMAGE} AS builder
ARG TARGETARCH
ENV APP_PATH=/dfnWorks
WORKDIR $APP_PATH

# Copy ONLY the C++ sources. This layer stays cached unless the C++ changes,
# so editing Python never triggers a recompile.
COPY DFNGen ./DFNGen
COPY DFNTrans ./DFNTrans
COPY DFN_Mesh_Connectivity_Test ./DFN_Mesh_Connectivity_Test

RUN <<'EOF'
set -eux
mkdir -p /out/bin

make -C DFNGen clean
make -C DFNGen -j"$(nproc)"
cp DFNGen/DFNGen /out/bin/DFNGen

make -C DFNTrans clean
make -C DFNTrans -j"$(nproc)"
cp DFNTrans/DFNTrans /out/bin/DFNTrans

make -C DFN_Mesh_Connectivity_Test clean
make -C DFN_Mesh_Connectivity_Test
cp DFN_Mesh_Connectivity_Test/ConnectivityTest /out/bin/ConnectivityTest
EOF

# ===========================================================================
# Stage 2 -- final runtime image
# ===========================================================================
FROM ${DEPS_IMAGE} AS final
ARG TARGETARCH

LABEL org.opencontainers.image.title="dfnWorks" \
      org.opencontainers.image.url="https://dfnworks.lanl.gov" \
      org.opencontainers.image.vendor="Triad National Security, LLC"

ENV APP_PATH=/dfnWorks \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1
WORKDIR $APP_PATH

# 1) Python deps first -- cached unless requirements.txt changes.
#    (Most of these are already pre-baked in the core image, so this is
#     usually a fast no-op of cache hits.)
COPY pydfnworks/requirements.txt pydfnworks/requirements.txt
RUN python3 -m pip install -r pydfnworks/requirements.txt

# 2) pydfnworks itself -- THIS is the "update on the fly" layer.
#    Change Python -> only this layer (and below) rebuild.
COPY pydfnworks ./pydfnworks
RUN python3 -m pip install ./pydfnworks

# 3) Compiled binaries from the builder stage. They merge into the bin/ that
#    already holds pflotran/lagrit/fehm from the core image.
COPY --from=builder /out/bin/ ./bin/

# 4) Output-report figures.
RUN <<'EOF'
set -eux
mkdir -p lib/figures
fig=pydfnworks/pydfnworks/dfnGen/generation/output_report/figures
cp "$fig/dfnWorks.all.black.png" lib/figures/
cp "$fig/lanl-logo-footer.png"   lib/figures/
EOF

# NOTE: the final image deliberately does NOT contain the C++ source trees,
# .git, docs, etc. (they stayed in the builder stage). If you also want the
# repo's examples/tests available at runtime, add an explicit COPY for them,
# e.g.:  COPY tests ./tests
#        COPY examples ./examples

CMD ["bash"]
