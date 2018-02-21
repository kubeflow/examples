# Kubeflow End to End

This example guides you through the process of taking a distributed model, modifying it to work with the tf-operator, providing data to your model, and serving the resulting trained model. We will be using Argo to manage the workflow, Kube Volume Controller to supply data via s3, and Kubeflow to serve the model.

## Prepare model

There is a delta between existing distributed mnist examples and the typical tfjob spec. This can be summarized with the following diff:

(link to github diff of stock mnist and modify mnist)

Basically, we must

1. Add handling for the tfjob Master
2. Convert the model itself to be importable as a python module
3. Make the download functionality configurable
4. Add an option to control the training directory

TODO: change all cluster spec stuff to just natively parse tfjob.

The resulting model is model.py.

### How to interface with TFJob

The stock grpc example expects the cluster spec to be provided via command line flags. We have modified  
show diff between mnist starting point and tfjob-ready mnist

explain how to shim out all junk except the actual model

## Upload data

Show how to upload to s3 bucket

## Preparing your Kubernetes Cluster

Provide links to GKE or EKS, assumption is that you have a cluster

### Deploying Tensorflow Operator

```
ks blah blah
```

### Deploying Argo


### Deploying Kube Volume Manager

```
helm blah blah
```

## Defining your training workflow

How to modify the basic argo templawte

```
dat: yaml
```

## Submitting your training workflow

## Monitoring

### dashboard

### tensorflow visualizer


## Serving your model

???
