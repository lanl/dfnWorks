# dfnWorks — Docker builds

Multi-arch (`linux/amd64` + `linux/arm64`) container builds for dfnWorks,
split into two images so the expensive dependencies are built **once** and the
fast-moving `pydfnworks` layer can be rebuilt on the fly.

## Layout

```
.
├── docker/
│   ├── build-core.dockerfile        # heavy deps: PETSc, PFLOTRAN, FEHM, LaGriT + Python
│   └── build-dfnworks.dockerfile    # thin app: pydfnworks + DFN C++ tools
├── docker-bake.hcl                  # one-command builds for both images
└── .dockerignore                    # keeps the app build context lean
```

## The two images

| Image | Built from | Contents | Rebuild cadence |
|-------|-----------|----------|-----------------|
| `dfn-deps` (core) | `ubuntu:24.04` | OS toolchain, Python stack, and source-compiled PETSc, PFLOTRAN, FEHM, LaGriT | Rarely — only when dependencies change |
| `dfnworks` (app) | `dfn-deps` | `pydfnworks` + compiled DFNGen / DFNTrans / ConnectivityTest | Constantly — every `pydfnworks` change |

The core is slow to build (everything is compiled from source). The app image
is a thin layer on top: it pulls the already-built core from the registry and
only rebuilds the Python package and the small C++ tools.

### Why it's structured this way

- **Pinned base** — `ubuntu:24.04` (noble) ships `gcc`/`g++`/`gfortran-12` for
  both amd64 and arm64, so the same Dockerfile builds cleanly on each arch.
- **PETSc pinned to `v3.24.5`** — the version PFLOTRAN v6.0 lists as supported.
  PFLOTRAN itself is built from its default branch (matching the official Linux
  install docs). Bump these together when upstream moves.
- **Multi-stage app image** — the C++ source trees and `.git` are compiled in a
  builder stage and never land in the final image.
- **Layer ordering for fast iteration** — the app installs `requirements.txt`
  first, then the `pydfnworks` package last. Editing Python only invalidates the
  final pip layer; the C++ compile and dependency layers stay cached.

## Prerequisites

- Docker with `buildx` (Docker 23+ / Docker Desktop).
- A registry you can push to (examples below use `ees16` on Docker Hub — swap
  in your own).

One-time builder setup (skip the `binfmt` line on Docker Desktop, which already
bundles QEMU):

```bash
docker run --privileged --rm tonistiigi/binfmt --install arm64,amd64
docker buildx create --name dfn --driver docker-container --bootstrap --use
docker login
```

> Multi-arch manifests must be **pushed**, not loaded — there is no local
> multi-platform image. Use `--load` only for a single-arch local test.

## Build with bake (recommended)

`docker-bake.hcl` encodes the platforms, tags, and the core→app relationship.

```bash
docker buildx bake core --push     # build-once dependency image (slow)
docker buildx bake app  --push     # iterate on pydfnworks (fast)
docker buildx bake      --push     # both, from scratch
```

Override variables inline:

```bash
REGISTRY=myorg DEPS_TAG=2025-06 docker buildx bake core --push
```

The `app` target references the core **from the registry** via the
`DEPS_IMAGE` build arg rather than chaining to the `core` target — that's what
preserves "build the core once." `bake app` reuses the cached multi-arch base.

## Build with plain buildx

Run from the repo root. Note the two images use **different build contexts**:
the core copies nothing (tiny context), the app needs the repo root.

Core (rarely):

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/build-core.dockerfile \
  -t ees16/dfn-deps:latest \
  -t ees16/dfn-deps:$(date +%Y-%m-%d) \
  --push \
  docker/
```

App (often):

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/build-dfnworks.dockerfile \
  --build-arg DEPS_IMAGE=ees16/dfn-deps:latest \
  -t ees16/dfnworks:latest \
  --push \
  .
```

Single-arch local test (can be `--load`ed):

```bash
docker buildx build --platform linux/amd64 \
  -f docker/build-dfnworks.dockerfile \
  --build-arg DEPS_IMAGE=ees16/dfn-deps:latest \
  -t dfnworks:dev --load .
```

## Don't emulate the core build

The app image builds fine under QEMU (just pip + small C++ compiles). The
**core** compiles PETSc, MPICH, HDF5, ParMETIS, and LaGriT — building the arm64
half under emulation on an amd64 host is extremely slow and MPICH sometimes
fails outright. Build each arch on native hardware and let buildx stitch the
manifest.

Add a native arm64 node to the same builder over SSH:

```bash
docker buildx create --name dfn --driver docker-container --use          # amd64 host
docker buildx create --append --name dfn --node dfn-arm ssh://user@arm-box
```

With both nodes attached, a multi-platform `buildx build`/`bake` runs each
platform on its native node — no emulation. (A CI matrix with native amd64 and
arm64 runners achieves the same thing.)

## Running

```bash
docker run --rm -it ees16/dfnworks:latest
```

Docker automatically pulls the image matching the host architecture from the
multi-arch manifest. The container drops into `bash` with `bin/` on `PATH` and
a `~/.dfnworksrc` pointing at the bundled executables:

| Key | Path |
|-----|------|
| `PETSC_DIR` | `/dfnWorks/lib/petsc` |
| `PETSC_ARCH` | `arch-linux-c-opt` |
| `PFLOTRAN_EXE` | `/dfnWorks/bin/pflotran` |
| `LAGRIT_EXE` | `/dfnWorks/bin/lagrit` |
| `FEHM_EXE` | `/dfnWorks/bin/fehm` |
| `PYTHON_EXE` | `/usr/bin/python3` |

To work on your own files, mount a host directory:

```bash
docker run --rm -it -v "$PWD":/work -w /work ees16/dfnworks:latest
```

## Maintenance notes

- **Updating dependencies** — edit `docker/build-core.dockerfile`, rebuild and
  push the core, then rebuild the app on top of it.
- **PETSc / PFLOTRAN versions** — keep the PETSc tag aligned with PFLOTRAN's
  "supported version" note in its
  [Linux install docs](https://documentation.pflotran.org/user_guide/how_to/installation/linux.html).
- **HDF5 zlib compression** — optional; add
  `--download-hdf5-configure-arguments="--with-zlib=yes"` to the PETSc
  `./configure` line in the core Dockerfile if you need compressed output.
- **Pin tags in production** — replace `:latest` with a dated tag
  (e.g. `dfn-deps:2025-06`) for reproducible builds.
- **Examples/tests in the image** — the app image is lean and does not ship the
  repo's `examples/` or `tests/`. Add explicit `COPY` lines in
  `build-dfnworks.dockerfile` if you want them baked in.
