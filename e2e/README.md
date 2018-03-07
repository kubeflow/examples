# Kubeflow End to End - Part 1

This example guides you through the process of taking a distributed model, modifying it to work with the tf-operator, providing data to your model, and serving the resulting trained model. We will be using Argo to manage the workflow, Kube Volume Controller to supply data via s3, and Kubeflow to serve the model.

## Prerequisites
To get started you need the following:
- A 1.9 Kubernetes cluster with RBAC
- S3-compatabile object store ([Amazon S3](https://aws.amazon.com/s3/), [Google Storage](https://cloud.google.com/storage/docs/interoperability), [Minio](https://www.minio.io/kubernetes.html))

You also need the following command line tools:
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [argo](https://github.com/argoproj/argo/blob/master/demo.md#1-download-argo)
- [helm](https://docs.helm.sh/using_helm/#installing-helm)
- [ksonnet](https://ksonnet.io/#get-started)

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
For our case we will be creating one single image which will serve master, workers and Parameter servers. feel free to create different images if that's what you need.
```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_BASE_URL}/mytfmodel:1.0

docker push ${DOCKER_BASE_URL}/mytfmodel:1.0
```

Alternately, you can use these existing images:

- gcr.io/kubeflow/mytfmodel:1.0

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
aws s3 mb s3://...
```

Now upload your training data

```
#Note if not using AWS S3, you must specify --endpoint-url
aws cp --recursive /tmp/mnistdata s3://...
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, Argo, and Kubernetes Volume Manager to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `tfworkflow`:

### Deploying Tensorflow Operator

We are using the tensorflow operator to automate our distributed training. The easiest way to install the operator is by using ksonnet:

Make sure you export your github token first `export GITHUB_TOKEN=xxxxxxxx`
```
NAMESPACE=tfworkflow
kubectl create namespace ${NAMESPACE}
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
$ kubectl logs -l name=tf-job-operator -n ${NAMESPACE}
...
I0226 18:25:16.553804       1 leaderelection.go:184] successfully acquired lease default/tf-operator
I0226 18:25:16.554615       1 controller.go:132] Starting TFJob controller
I0226 18:25:16.554630       1 controller.go:135] Waiting for informer caches to sync
I0226 18:25:16.654781       1 controller.go:140] Starting %v workers1
I0226 18:25:16.654813       1 controller.go:146] Started workers
...
$ kubectl get crd
NAME                    AGE
tfjobs.kubeflow.org     22m
```

### Deploying Argo

Argo is a workflow system used to automate workloads on Kubernetes.

```
NAMESPACE=tfworkflow
argo install --install-namespace ${NAMESPACE}
```

We can check on the status of Argo by checking the logs and listing workflows.

```
$ kubectl logs -l app=workflow-controller -n ${NAMESPACE}
time="2018-02-26T18:35:48Z" level=info msg="workflow controller configuration from workflow-controller-configmap:\nexecutorImage: argoproj/argoexec:v2.0.0-beta1"
time="2018-02-26T18:35:48Z" level=info msg="Workflow Controller (version: v2.0.0-beta1) starting"
time="2018-02-26T18:35:48Z" level=info msg="Watch Workflow controller config map updates"
time="2018-02-26T18:35:48Z" level=info msg="Detected ConfigMap update. Updating the controller config."
time="2018-02-26T18:35:48Z" level=info msg="workflow controller configuration from workflow-controller-configmap:\nexecutorImage: argoproj/argoexec:v2.0.0-beta1"
time="2018-02-26T18:40:48Z" level=info msg="Alloc=2623 TotalAlloc=45740 Sys=11398 NumGC=20 Goroutines=50"
$ argo list
NAME   STATUS   AGE   DURATION
```

Lastly we need to modify the argo cluster role used to run the workflow. We need to do this in order to create tfjobs and volumemanagers:
```
kubectl apply -f argo-cluster-role.yaml
```

### Deploying Kube Volume Controller

Kube Volume Controller is a utility that can seed replicas of datasets across nodes.

First we need to install tiller on the cluster with rbac. Instructions can be found [here](https://github.com/kubernetes/helm/blob/master/docs/rbac.md).

Then install Kube Volume Controller:
```
NAMESPACE=tfworkflow
git clone https://github.com/kubeflow/experimental-kvc.git
cd kube-volume-controller
helm install helm-charts/kube-volume-controller/ -n kvc --wait \
  --set clusterrole.install=true \
  --set storageclass.install=true \
  --set namespace=${NAMESPACE}
cd ..
```

We can check on the status of kube-volume-controller:
```
$ kubectl get pod -l=app=kube-volume-controller
NAME                                      READY     STATUS    RESTARTS   AGE
kube-volume-controller-6586c65c4f-smdd4   1/1       Running   0          1d
$ kubectl get crd | grep volumemanagers
volumemanagers.aipg.intel.com                 17d
```

### Creating secrets for our workflow
For fetching and uploading data, our workflow requires some credentials to be stored as kubernetes secrets:
```
kubectl create secret generic aws-creds --from-literal=awsAccessKeyID=${AWS_ACCESS_KEY_ID} \
 --from-literal=awsSecretAccessKey=${AWS_SECRET_ACCESS_KEY}
```

## Defining your training workflow

This is the bulk of the work, let's walk through what is needed:

1. Download our datasets
2. Train the model
3. Export the model
4. Serve the model

Now let's look at how this is represented in our [example workflow](tfargo.yaml)

## Submitting your training workflow

First we need to set a few variables in our workflow. Make sure to set your docker registry or remove the `IMAGE` parameters in order to use our defaults:

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
export AWS_REGION=us-west-2
export AWS_ENDPOINT_URL=https://s3.us-west-2.amazonaws.com
export S3_ENDPOINT=s3.us-west-2.amazonaws.com
export S3_DATA_URL=s3://tfoperator/data/mnist/
export S3_TRAIN_BASE_URL=s3://tfoperator/models
export JOB_NAME=myjob-$(uuidgen  | cut -c -5 | tr '[:upper:]' '[:lower:]')
export TF_SERVER_IMAGE=${DOCKER_BASE_URL}/mytfmodel:1.0
export TF_MODEL_IMAGE=${DOCKER_BASE_URL}/mytfmodel:1.0
export NAMESPACE=tfworkflow
```

Next, submit your workflow.

```
argo submit tfargo.yaml -n ${NAMESPACE} --serviceaccount argo \
    -p aws-endpoint-url=${AWS_ENDPOINT_URL} \
    -p s3-endpoint=${S3_ENDPOINT} \
    -p aws-region=${AWS_REGION} \
    -p tf-server-image=${TF_SERVER_IMAGE} \
    -p tf-model-image=${TF_MODEL_IMAGE} \
    -p s3-data-url=${S3_DATA_URL} \
    -p s3-train-base-url=${S3_TRAIN_BASE_URL} \
    -p job-name=${JOB_NAME} \
    -p namespace=${NAMESPACE}
```

Your training workflow should now be executing.

You can verify and keep track of your workflow using the argo commands:
```
$ argo list -n ${NAMESPACE}
NAME                STATUS    AGE   DURATION
tf-workflow-h7hwh   Running   1h    1h

$ argo get tf-workflow-h7hwh -n ${NAMESPACE}
```

## Monitoring

There are various ways to visualize your workflow/training job.

### Argo UI

The Argo UI is useful for seeing what stage your worfklow is in:

```
NAMESPACE=tfworkflow
PODNAME=$(kubectl get pod -l app=argo-ui -n${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${PODNAME} 8001:8001 -n${NAMESPACE}
```

### Tensorboard

Tensorboard is deployed after training is done. To connect:

```
NAMESPACE=tfworkflow
PODNAME=$(kubectl get pod -n${NAMESPACE} -l app=tensorboard-${JOB_NAME} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${PODNAME} 6006:6006 -n${NAMESPACE}
```

## Using Tensorflow serving

Once the workflow has completed, your model should be serving.

TODO modify mnist client to use invidiual number images, seems more exciting than just submitting a batch of files.

```
NAMESPACE=tfworkflow
POD_NAME=$(kubectl get pod -l=app=${JOB_NAME} -n${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward -n${NAMESPACE} ${POD_NAME} -p 9000:9000
python mnist_client.py  --server 127.0.0.1:9000 --data_dir /tmp/mnistdata
```

## Next Steps

As you noticed, there were many portions of this example that are shimming functionality around data. In the next part, we will be modifying these examples further to directly utilize object stores.
