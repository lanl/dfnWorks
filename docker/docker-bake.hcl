# docker-bake.hcl  --  place at the repo root, run with `docker buildx bake`
#
#   docker buildx bake core --push      # build-once dependency image (slow)
#   docker buildx bake app  --push      # iterate on pydfnworks (fast)
#   docker buildx bake      --push      # both, from scratch
#
# Override any variable inline, e.g.:
#   REGISTRY=myorg DEPS_TAG=2025-06 docker buildx bake core --push

variable "REGISTRY" { default = "ees16" }
variable "DEPS_TAG" { default = "latest" }
variable "APP_TAG"  { default = "latest" }
variable "PLATFORMS" {
  default = ["linux/amd64", "linux/arm64"]
}

group "default" {
  targets = ["core", "app"]
}

# Heavy dependency image: PETSc / PFLOTRAN / FEHM / LaGriT + Python stack.
# Build this once and push it; the app target consumes it from the registry.
target "core" {
  context    = "docker"
  dockerfile = "build-core.dockerfile"
  platforms  = PLATFORMS
  tags = [
    "${REGISTRY}/dfn-deps:${DEPS_TAG}",
  ]
  # SBOM/provenance attestations can add "unknown/unknown" manifest entries
  # on some registries; disable if your registry chokes on them.
  # provenance = false
}

# Thin application image: pydfnworks + the small DFN C++ tools.
# Pulls the (already-pushed) core image as its base, so this stays fast.
target "app" {
  context    = "."
  dockerfile = "docker/build-dfnworks.dockerfile"
  platforms  = PLATFORMS
  args = {
    DEPS_IMAGE = "${REGISTRY}/dfn-deps:${DEPS_TAG}"
  }
  tags = [
    "${REGISTRY}/dfnworks:${APP_TAG}",
  ]
}
