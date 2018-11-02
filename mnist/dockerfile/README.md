# Dockerfiles

These two Dockerfiles are used to build ksonnect and mnist model docker images.

TODO: Need to move these dockerfiles to kubeflow offical place, details here: https://github.com/kubeflow/examples/issues/319


## ksonnect

```
docker build -t siji/ksonnet:v0.13.0 -f Dockerfile.ksonnet .
```


## mnist model

```
docker build -t siji/mnist-model:v1.11.0 -f Dockerfile.model .
```
