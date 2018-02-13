# Demo container

This directory contains a Dockerfile, build.sh script, demo notebook, and various related assets. The demonstration container can be built and pushed to Google Container Registry with the following command:

```bash
sh build.sh
```

At which point it can be used in the manner described in the main readme for this example. If the demo container is to be used by users without permissions to the project owning the container registry then either this registry needs to be made public or the container needs to be pushed to an alternative public registry.
