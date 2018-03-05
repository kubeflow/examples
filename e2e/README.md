# Kubeflow End to End - Part 1

This example guides you through the process of taking a distributed model, modifying it to work with the tf-operator, providing data to your model, and serving the resulting trained model. We will be using Argo to manage the workflow, Kube Volume Controller to supply data via s3, and Kubeflow to serve the model.

## Prerequisites

- A 1.9 Kubernetes cluster with RBAC
- S3-compatabile object store ([Amazon S3](https://aws.amazon.com/s3/), [Google Storage](https://cloud.google.com/storage/docs/interoperability), [Minio](https://www.minio.io/kubernetes.html))
- Clis for [Argo](https://github.com/argoproj/argo/blob/master/demo.md#1-download-argo), [Ksonnet](https://github.com/ksonnet/ksonnet#install), [Helm](https://github.com/kubernetes/helm/blob/master/docs/install.md#installing-the-helm-client), [S3](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)

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
mkdir -p /tmp/mnistdata
cd /tmp/mnistdata

curl -O https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz
curl -O https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz
curl -O https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz
curl -O https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz
```

Next create a bucket or path in your S3-compatible object store.

```
aws mb s3://...
```

Now upload your training data

```
#Note if not using AWS S3, you must specify --endpoint-url
aws cp --recursive /tmp/mnistdata s3://...
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, Argo, and Kubernetes Volume Manager to help manage our training job.

### Deploying Tensorflow Operator

We are using the tensorflow operator to automate our distributed training. The easiest way to install the operator is by using ksonnet:

```
APP_NAME=my-kubeflow
ks init ${APP_NAME}
cd ${APP_NAME}

#todo pin this to a tag
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/1a6fc9d0e19e456b784ba1c23c03ec47648819d0/kubeflow

ks pkg install kubeflow/core@1a6fc9d0e19e456b784ba1c23c03ec47648819d0
ks pkg install kubeflow/tf-serving@1a6fc9d0e19e456b784ba1c23c03ec47648819d0
ks pkg install kubeflow/tf-job@1a6fc9d0e19e456b784ba1c23c03ec47648819d0

# Deploy Kubeflow
NAMESPACE=kubeflow
kubectl create namespace ${NAMESPACE}
ks generate core kubeflow-core --name=kubeflow-core --namespace=${NAMESPACE}
ks apply default -c kubeflow-core
```

Check to ensure things have deployed:

```
$ kubectl logs -l name=tf-job-operator
...
I0226 18:25:16.553804       1 leaderelection.go:184] successfully acquired lease default/tf-operator
I0226 18:25:16.554615       1 controller.go:132] Starting TFJob controller
I0226 18:25:16.554630       1 controller.go:135] Waiting for informer caches to sync
I0226 18:25:16.654781       1 controller.go:140] Starting %v workers1
I0226 18:25:16.654813       1 controller.go:146] Started workers
...
$ kubectl  get crd
NAME                    AGE
tfjobs.kubeflow.org     22m
```

### Deploying Argo

Argo is a workflow system used ot automate workloads on Kubernetes. This is what will tie the room together.

```
#TODO see if argo's being installed by kubeflow yet
ks pkg install kubeflow/argo
ks prototype use io.ksonnet.pkg.argo argo --namespace default --name argo
ks apply default -c argo
```

We can check on the status of Argo by checking the logs and listing workflows.

```
$ kubectl  logs -l app=workflow-controller
time="2018-02-26T18:35:48Z" level=info msg="workflow controller configuration from workflow-controller-configmap:\nexecutorImage: argoproj/argoexec:v2.0.0-beta1"
time="2018-02-26T18:35:48Z" level=info msg="Workflow Controller (version: v2.0.0-beta1) starting"
time="2018-02-26T18:35:48Z" level=info msg="Watch Workflow controller config map updates"
time="2018-02-26T18:35:48Z" level=info msg="Detected ConfigMap update. Updating the controller config."
time="2018-02-26T18:35:48Z" level=info msg="workflow controller configuration from workflow-controller-configmap:\nexecutorImage: argoproj/argoexec:v2.0.0-beta1"
time="2018-02-26T18:40:48Z" level=info msg="Alloc=2623 TotalAlloc=45740 Sys=11398 NumGC=20 Goroutines=50"
$ argo list
NAME   STATUS   AGE   DURATION
```

### Deploying Kube Volume Manager

Kube Volume Manager is a utility that can seed replicas of datasets across nodes.

```
#TODO change to plain http based on github releases once we're open source
aws s3 cp s3://helm-packages/kube-volume-controller-v0.1.0.tgz ./
helm install kube-volume-controller-v0.1.0.tgz
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
export AWS_REGION=us-west-2
export AWS_ENDPOINT_URL=https://s3.us-west-2.amazonaws.com
export S3_ENDPOINT=s3.us-west-2.amazonaws.com
export S3_DATA_URL=s3://tfoperator/data/mnist/
export S3_TRAIN_BASE_URL=s3://tfoperator/models
export JOB_NAME=myjob-$(uuidgen  | cut -c -5 | tr '[:upper:]' '[:lower:]')
export TF_SERVER_IMAGE=elsonrodriguez/mytfserver:1.6
export MODEL_IMAGE=elsonrodriguez/mytfmodel:1.45
export NAMESPACE=demo
```

Next, submit your workflow.

```
argo submit tfargo.yaml -n ${NAMESPACE} --serviceaccount argo \
    -p aws-endpoint-url=${AWS_ENDPOINT_URL} \
    -p s3-endpoint=${S3_ENDPOINT} \
    -p aws-region=${AWS_REGION} \
    -p tf-server-image=${TF_SERVER_IMAGE} \
    -p model-image=${MODEL_IMAGE} \
    -p s3-data-url=${S3_DATA_URL} \
    -p s3-train-base-url=${S3_TRAIN_BASE_URL} \
    -p job-name=${JOB_NAME} \
    -p namespace=${NAMESPACE}
```

Your training workflow should now be executing.

## Monitoring

There are various ways to visualize your workflow/training job.

### Argo UI

The Argo UI is useful for seeing what stage your worfklow is in:

```
PODNAME=$(kubectl get pod -l app=argo-ui -nargo -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${PODNAME} 8001:8001 -n argo
```

### Tensorboard

Tensorboard is deployed after training is done. To connect:

```
PODNAME=$(kubectl get pod -l app=tensorboard-${JOB_NAME}
kubectl port-forward ${PODNAME} 6006:6006 -n argo
```

## Using Tensorflow serving

Once the workflow has completed, your model should be serving.

TODO modify mnist client to use invidiual number images, seems more exciting than just submitting a batch of files.

```
POD_NAME=`kubectl get pod -l=app=${JOB_NAME}`
kubectl port-forward ${POD_NAME} -p 9000:9000
python mnist_client.py  --server localhost:9000 --data_dir /tmp/mnistdata
```

## Next Steps

As you noticed, there were many portions of this example that are shimming functionality around data. In the next part, we will be modifying these examples further to directly utilize object stores.
