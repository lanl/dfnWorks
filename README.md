# README

For information on how to get dfnWorks up and running, please see the document dfnWorks.pdf, in this directory.

# Using Docker

To build a Docker image, run

    docker build -t dfnworks .

This will take 45 - 60 minutes to complete.

After completion, you can launch `bash` (the default command) in the Docker
container by running:

    docker run -ti --name NAME dfnworks:latest

While docker run is still live, you can execute an arbitrary command with 

    docker exec -i -t NAME COMMAND

where `COMMAND` is the command, such as `python`, `ls`, etc, and `NAME` is
an arbitrary name for this instance (i.e., `dfn`).

(*Note:* if you are doing many dfnWorks Docker builds, you may have dangling
images taking up disk space. Use `docker system prune` to clean them)

## Note: Proxy issues

If download via Git or `apt-get` fails during build, ensure that your Docker 
config file (`~/.docker/config.json`) has proxy information set.

For example, my proxy file looks like:

```
{
    "auths": {
        "https://index.docker.io/v1/": {}
    },
    "HttpHeaders": {
        "User-Agent": "Docker-Client/18.09.2 (darwin)"
    },
    "credsStore": "osxkeychain",
    "stackOrchestrator": "swarm",
    "proxies": {
        "default": {
            "httpProxy": "http://proxyout.lanl.gov:8080",
            "httpsProxy": "http://proxyout.lanl.gov:8080"
        }
    }
}
```

In addition, you may have to also change proxy settings under 
*Docker -> Preferences -> Proxies -> Manual proxy configuration*.