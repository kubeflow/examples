# Kubeflow End to End

This example guides you through the process of taking a distributed model, modifying it to work with the tf-operator, providing data to your model, and serving the resulting trained model. We will be using Argo to manage the workflow, Kube Volume Controller to supply data via S3, and Kubeflow to serve the model.

## Prerequisites

Before we get started there a few requirements.

### Kubernetes Cluster Environment

Your cluster must:

- Be at least version 1.9
- Have access to an S3-compatible object store ([Amazon S3](https://aws.amazon.com/s3/), [Google Storage](https://cloud.google.com/storage/docs/interoperability), [Minio](https://www.minio.io/kubernetes.html))
- Contain 3 nodes of at least 8 cores and 16 GB of RAM.

If using GKE, the following will provision a cluster with the required features:

```
export CLOUDSDK_CONTAINER_USE_CLIENT_CERTIFICATE=True
gcloud alpha container clusters create ${USER} --enable-kubernetes-alpha --machine-type=n1-standard-8 --num-nodes=3 --disk-size=200 --zone=us-west1-a --cluster-version=1.9.2-gke.1 --image-type=UBUNTU
```

### Local Setup

You also need the following command line tools:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [argo](https://github.com/argoproj/argo/blob/master/demo.md#1-download-argo)
- [helm](https://docs.helm.sh/using_helm/#installing-helm)
- [ksonnet](https://ksonnet.io/#get-started)
- [aws](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)
- [minio client](https://github.com/minio/mc#macos)

## Modifying existing examples

Many examples online use containers with pre-canned data, or scripts with certain assumptions as to the cluster spec. We will modify one of these [examples](https://github.com/tensorflow/tensorflow/tree/0375ffcf83e16c3d6818fa67c9c13de810c1dacf/tensorflow/tools/dist_test) to work with the tensorflow operator, and to work more like a real-world example.

### Prepare model

There is a delta between existing distributed mnist examples and what's needed to run well as a TFJob. These changes can be viewed in the [included diff](mnist-changes.md)

Basically, we must

1. Add handling for the tfjob Master
2. Convert the model itself to be importable as a python module
3. Save the graph in a way that's exportable
4. Add an option to control the training directory

TODO: Verify that all the changes were neccessary, especially #3
TODO: Had to disable master handling... probably save it for a future update.

The resulting model is [model.py](model.py).

### Prepare distribued tensorflow grpc components.

The stock distributed Tensorflow [examples](https://github.com/tensorflow/tensorflow/blob/3af03be757b63ea6fbd28cc351d5d2323c526354/tensorflow/tools/dist_test/server/grpc_tensorflow_server.py) expect the cluster spec to be provided via command line arguments. We have modified an [existing shim](https://github.com/kubeflow/kubeflow/blob/d5caf230ff50260c1a6565db35edeeddd5d407e6/tf-controller-examples/tf-cnn/launcher.py) to be more [generic](tf_job_shim.py), and will be wrapping the standard examples in order to process TF_CONFIG into something it understands.

### Build and push images.

With our code ready, we will now build/push the docker images

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
docker build . --no-cache  -f Dockerfile.tfserver -t ${DOCKER_BASE_URL}/mytfserver:1.0
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_BASE_URL}/mytfmodel:1.0

docker push ${DOCKER_BASE_URL}/mytfserver:1.0
docker push ${DOCKER_BASE_URL}/mytfmodel:1.0
```

Alternately, you can use these existing images:

- gcr.io/kubeflow/mytfserver:1.0
- gcr.io/kubeflow/mytfmodel:1.0

TODO: Actually put images at these urls, or replace with another url.
## Upload data

First, we need to grab the mnist training data set:

```
mkdir -p /tmp/mnistdata
cd /tmp/mnistdata

curl -O https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz
curl -O https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz
curl -O https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz
curl -O https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz
cd -
```

Next create a bucket or path in your S3-compatible object store.

```
#Note if not using AWS S3, you must specify --endpoint-url for all these commands.
BUCKET_NAME=mybucket
aws s3api create-bucket --bucket=${BUCKET_NAME}
```

Now upload your training data

```
export S3_ENDPOINT=s3.us-west-2.amazonaws.com
export AWS_ENDPOINT_URL=https://${S3_ENDPOINT}
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx

mc config host add s3 ${AWS_ENDPOINT_URL} ${AWS_ACCESS_KEY_ID} ${AWS_SECRET_ACCESS_KEY}
mc mirror /tmp/mnistdata/ s3/${BUCKET_NAME}/data/mnist/
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, Argo, and Kubernetes Volume Manager to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `tfworkflow`:

### Deploying Tensorflow Operator

We are using the tensorflow operator to automate our distributed training. The easiest way to install the operator is by using ksonnet:

Make sure you export your github token first `export GITHUB_TOKEN=xxxxxxxx`. And since you will need admin status for the final `ks apply` command, make sure you are an admin of the cluster `kubectl config set-credentials ...`, `kubectl config set-context ...` then `kubectl config use-context ...`.
```
NAMESPACE=tfworkflow
APP_NAME=my-kubeflow
ks init ${APP_NAME}
cd ${APP_NAME}

#todo pin this to a tag
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/1a6fc9d0e19e456b784ba1c23c03ec47648819d0/kubeflow

ks pkg install kubeflow/core@1a6fc9d0e19e456b784ba1c23c03ec47648819d0
ks pkg install kubeflow/tf-serving@1a6fc9d0e19e456b784ba1c23c03ec47648819d0
ks pkg install kubeflow/tf-job@1a6fc9d0e19e456b784ba1c23c03ec47648819d0

# Deploy Kubeflow
kubectl create namespace ${NAMESPACE}
ks generate core kubeflow-core --name=kubeflow-core --namespace=${NAMESPACE}
ks apply default -c kubeflow-core

# Switch context for the rest of the example
kubectl config set-context $(kubectl config current-context) --namespace=${NAMESPACE}
cd -
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
$ kubectl get crd
NAME                    AGE
tfjobs.kubeflow.org     22m
```

### Deploying Argo

Argo is a workflow system used to automate workloads on Kubernetes. The Argo cli can automatically install argo on your Kubernetes cluster.

```
argo install --install-namespace=${NAMESPACE}
```

We can check on the status of Argo by checking the logs and listing workflows.

```
$ kubectl logs -l app=workflow-controller
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

Kube Volume Controller is a utility that can seed replicas of datasets across nodes. Think of it as an explicit caching mechanism.

First we need to install tiller on the cluster with rbac under the kube-system namespace. Instructions can be found [here](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#example-service-account-with-cluster-admin-role) in the section "Example: Service account with cluster-admin role".

Then install Kube Volume Controller:
```
git clone https://github.com/kubeflow/experimental-kvc.git
cd experimental-kvc
git checkout 753e309b
helm install helm-charts/kube-volume-controller/ -n kvc --wait \
  --set clusterrole.install=true \
  --set storageclass.install=true \
  --set tag=753e309 \
  --set namespace=${NAMESPACE}
cd ..
```

We can check on the status of kube-volume-controller:
```
$ kubectl get pod -l=app=kvc
NAME                   READY     STATUS    RESTARTS   AGE
kvc-765bf7f8f7-r9nmb   1/1       Running   0          40s
$ kubectl get crd | grep volumemanagers
volumemanagers.kvc.kubeflow.org   1m
```

### Creating secrets for our workflow
For fetching and uploading data, our workflow requires S3 credentials. These credentials will be provided as kubernetes secrets:
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

Now let's look at how this is represented in our [example workflow](model-train.yaml)

## Submitting your training workflow

First we need to set a few variables in our workflow. Make sure to set your docker registry or remove the `IMAGE` parameters in order to use our defaults:

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
export S3_ENDPOINT=s3.us-west-2.amazonaws.com
export S3_DATA_URL=s3://${BUCKET_NAME}/data/mnist/
export S3_TRAIN_BASE_URL=s3://${BUCKET_NAME}/models
export AWS_ENDPOINT_URL=https://${S3_ENDPOINT}
export AWS_REGION=us-west-2
export JOB_NAME=myjob-$(uuidgen  | cut -c -5 | tr '[:upper:]' '[:lower:]')
export TF_MODEL_IMAGE=${DOCKER_BASE_URL}/mytfmodel:1.0
export NAMESPACE=tfworkflow
export TF_WORKER=3
export MODEL_TRAIN_STEPS=200
```

Next, submit your workflow.

```
argo submit model-train.yaml -n ${NAMESPACE} --serviceaccount argo \
    -p aws-endpoint-url=${AWS_ENDPOINT_URL} \
    -p s3-endpoint=${S3_ENDPOINT} \
    -p aws-region=${AWS_REGION} \
    -p tf-model-image=${TF_MODEL_IMAGE} \
    -p s3-data-url=${S3_DATA_URL} \
    -p s3-train-base-url=${S3_TRAIN_BASE_URL} \
    -p job-name=${JOB_NAME} \
    -p tf-worker=${TF_WORKER} \
    -p model-train-steps=${MODEL_TRAIN_STEPS} \
    -p namespace=${NAMESPACE}
```

Your training workflow should now be executing.

You can verify and keep track of your workflow using the argo commands:
```
$ argo list
NAME                STATUS    AGE   DURATION
tf-workflow-h7hwh   Running   1h    1h

$ argo get tf-workflow-h7hwh
```

## Monitoring

There are various ways to monitor workflow/training job. In addition to using `kubectl` to query for the status of `pods`, you can see the status of the mnist data volume:

```
kubectl describe volumemanager mnist

```

Some basic dashboards are also available.

### Argo UI

The Argo UI is useful for seeing what stage your worfklow is in:

```
PODNAME=$(kubectl get pod -l app=argo-ui -n${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${PODNAME} 8001:8001
```

You should now be able to visit [http://127.0.0.1:8001](http://127.0.0.1:8001) to see the status of your workflows.

### Tensorboard

Tensorboard is deployed just before training starts. To connect:

```
PODNAME=$(kubectl get pod -l app=tensorboard-${JOB_NAME} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${PODNAME} 6006:6006
```

Tensorboard can now be accessed at [http://127.0.0.1:6006](http://127.0.0.1:6006).

## Using Tensorflow serving

By default the workflow deploys our model via Tensorflow Serving. Included in this example is a client that can query your model and provide results:

TODO modify mnist client to use invidiual number images, seems more exciting than just submitting a batch of files.

```
POD_NAME=$(kubectl get pod -l=app=mnist-${JOB_NAME} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${POD_NAME} 9000:9000 &
python mnist_client.py  --server 127.0.0.1:9000 --data_dir /tmp/mnistdata/
```

Model serving can be turned off by passing in `-p model-serving=false` to the `model-train.yaml` workflow. If you wish to serve your model after training, use the `model-deploy.yaml` workflow. Simply pass in the desired finished argo workflow as an argument:

```
WORKFLOW=<the workflowname>
argo submit model-deploy.yaml -n ${NAMESPACE} -p workflow=${WORKFLOW} --serviceaccount=argo
```

## Stopping and resubmitting your workflow

If you want to rerun your workflow with changes or for debugging purposes, delete all of the tfjobs and volumemanagers with `kubectl delete tfjob --all` and `kubectl delete volumemanagers --all`. Then, you will need to provide a new, unique job-name when resubmitting the workflow, by either using the `job-name=<new-value>` option in the `argo submit` command or editing the job-name value in model_train.yaml.

## Next Steps

In the future we will be providing tutorials on more advanced examples.

Till then, play with the settings/tunables! And try to use your own model within this workflow.
