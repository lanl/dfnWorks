# Building a Docker container

Because the dependencies for dfnWorks may change much 
more frequently than dfnWorks does itself, and because 
the dependencies take significant compute time to build,
the Docker build process is segmented into two parts.


### `build-core.dockerfile`

This file builds the depdencies into its own container. This 
container is NOT pushed to DockerHub, but is kept on your local machine.

This container is intended to be updated infrequently.

**Usage:**

    docker build -t dfn-deps -f docker/build-core.dockerfile ./

### `build-dfnworks.dockerfile`

This Dockerfile constructs the final dfnWorks container, using
the `build-core` container as a starting image. 

**Usage:**

    docker build -t ees16/dfnworks:latest -f docker/build-dfnworks.dockerfile ./