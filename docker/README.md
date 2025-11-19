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

    docker buildx build --platform linux/amd64,linux/arm64 -t dfn-deps:latest -f docker/build-core.dockerfile ./

### `build-dfnworks.dockerfile`

This Dockerfile constructs the final dfnWorks container, using
the `build-core` container as a starting image. 




## Trouble shooting
If no space left on device run
    1. docker container prune
    2. docker image prune
    3. docker rmi $(docker images -q -f "dangling=true")
    4. docker rm $(docker ps -q -f 'status=exited')

##  Push to docker 
docker login --username=<username>
docker push ees16/dfnworks:latest

docker tag #image_id ees16/dfnworks:<v2.*>

**Usage:**

    docker buildx build --platform linux/amd64,linux/arm64 -t ees16/dfnworks:latest -f docker/build-dfnworks.dockerfile ./


