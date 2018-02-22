# Kubeflow End to End

This example guides you through the process of taking a distributed model, modifying it to work with the tf-operator, providing data to your model, and serving the resulting trained model. We will be using Argo to manage the workflow, Kube Volume Controller to supply data via s3, and Kubeflow to serve the model.

## Prerequisites

- A 1.9 Kubernetes cluster with RBAC
- S3-compatabile object store

## Modifying existing examples

Most examples online use containers with pre-canned data, or scripts with certain assumptions as to the cluster spec, we will modify one of these [examples](https://github.com/tensorflow/tensorflow/tree/0375ffcf83e16c3d6818fa67c9c13de810c1dacf/tensorflow/tools/dist_test) to work with the tensorflow operator, and to work more like a real-world example. 

### Prepare model

There is a delta between existing distributed mnist examples and the typical tfjob spec. This can be summarized with the following diff:

(link to github diff of stock mnist and modify mnist)
https://github.com/tensorflow/tensorflow/blob/0375ffcf83e16c3d6818fa67c9c13de810c1dacf/tensorflow/tools/dist_test/python/mnist_replica.py
https://github.com/elsonrodriguez/examples/blob/e2e/e2e/model.py

Basically, we must

1. Add handling for the tfjob Master
2. Convert the model itself to be importable as a python module
3. Make the download functionality configurable
4. Add an option to control the training directory

TODO: change all cluster spec stuff to just natively parse tfjob.

The resulting model is [model.py](model.py).

### Prepare distribued tensorflow grpc components.

The stock distributed tensorflow grpc [example](https://github.com/tensorflow/tensorflow/blob/3af03be757b63ea6fbd28cc351d5d2323c526354/tensorflow/tools/dist_test/server/grpc_tensorflow_server.py) expects the cluster spec to be provided via command line arguments. We have modified an [existing shim](https://github.com/kubeflow/kubeflow/blob/d5caf230ff50260c1a6565db35edeeddd5d407e6/tf-controller-examples/tf-cnn/launcher.py) to be more [generic](tf_job_shim.py), and will be wrapping the standard grpc server in order to process TF_CONFIG into something it understands.

### Build and push images.

With our code ready, we will now build/push the docker images

```
DOCKER_BASE_URL=docker.io/elsonrodriguez
docker build . --no-cache  -f Dockerfile.tfserver -t ${DOCKER_BASE_URL}/mytfserver:1.0
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_BASE_URL}/mytfmodel:1.0

docker push elsonrodriguez/mytserver:1.0
docker push elsonrodriguez/mytfmodel:1.0
```

Alternately, you can use these existing images:

- gcr.io/kubeflow/mytfserver:1.0
- gcr.io/kubeflow/mytmodel:1.0

## Upload data

First, we need to grab the mnist training data set:

```
curl ...
```

Next create a bucket or path in your S3-compatible object store.

```
aws mb...
```

Now upload your training data

```
aws cp..
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, no the cluster must be prepared. We will be deploying the TF Operator, Argo, and Kubernetes Volume Manager to help manage our training job.

### Deploying Tensorflow Operator

We are using the tensorflow operator to automate our distributed training. The easiest way to install the operator is by using ksonnet:

```
APP_NAME=my-kubeflow
ks init ${APP_NAME}
cd ${APP_NAME}

#todo pin this to a tag
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow

ks pkg install kubeflow/core
ks pkg install kubeflow/tf-serving
ks pkg install kubeflow/tf-job

# Deploy Kubeflow
NAMESPACE=kubeflow
kubectl create namespace ${NAMESPACE}
ks generate core kubeflow-core --name=kubeflow-core --namespace=${NAMESPACE}
ks apply default -c kubeflow-core
```

Check to ensure things have deployed:

```
kubectl ....
```

### Deploying Argo

Argo is a workflow system used ot automate workloads on Kubernetes. This is what will tie the room together.

```
ks...
```

We can check on the status of Argo by typing

```
argo ....
```

### Deploying Kube Volume Manager

Kube Volume Manager is a utility that can seed replicas of datasets across nodes.

```
helm .... 
```

And again verify
```
kubectl ...
```

## Defining your training workflow

This is the bulk of the work, let's walk through what is needed:

1. Download our datasets
2. Train the model
3. Export the model
4. Serve the model

Now let's look at how this is represented in our [example workflow](workflow.yaml)

```
dat: yaml
```
## Submitting your training workflow

First we need to set a few variables in our workflow.

```
TF_SERVER_IMAGE=docker.io/...
MODEL_IMAGE=docker.io/...
AWS_SECRET_ACCESS_KEY=
AWS_ACCESS_KEY_ID=
AWS_ENDPOINT_URL=http://
DATA_S3_URL=
TRAINING_S3_BASE_URL=

argo ...?
```

Your training workflow should now be executing.

## Monitoring

There are various ways to visualize what your workflow is doing.

### Argo UI

#TODO how to argo UI

### Tensorboard

TODO how to tensorboar 

## Serving your model

Once the workflow has completed, your model should be serving:

#TODO how to access model with an mnist client
