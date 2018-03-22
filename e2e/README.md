# Kubeflow End to End

This example guides you through the process of taking a distributed model, modifying it to work with the tf-operator, providing data to your model, and serving the resulting trained model. We will be using Argo to manage the workflow, Kube Volume Controller to locally cache data from S3, Tensorflow's S3 support for saving model training info, Tensorboard to visualize the training, and Kubeflow to serve the model.

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

NOTE: You must be a Kubernetes admin to follow this guide. If you are not an admin, please contact your local cluster administrator for a client cert, or credentials to pass into the following commands:

```
$ kubectl config set-credentials <username> --username=<admin_username> --password=<admin_password>
$ kubectl config set-context <context_name> --cluster=<cluster_name> --user=<username> --namespace=<namespace>
$ kubectl config use-context <context_name>
```

### Local Setup

You also need the following command line tools:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [argo](https://github.com/argoproj/argo/blob/master/demo.md#1-download-argo)
- [helm](https://docs.helm.sh/using_helm/#installing-helm)
- [ksonnet](https://ksonnet.io/#get-started)
- [aws](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)
- [minio client](https://github.com/minio/mc#macos)

NOTE: These instructions rely on Github, and may cause issues if behind a firewall with many Github users. Make sure you [generate and export this token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/):

```
export GITHUB_TOKEN=xxxxxxxx
```

## Modifying existing examples

Many examples online use containers with pre-canned data, or scripts with certain assumptions as to the cluster spec. We will modify one of these [examples](https://github.com/tensorflow/tensorflow/tree/0375ffcf83e16c3d6818fa67c9c13de810c1dacf/tensorflow/tools/dist_test) to work with the tensorflow operator, and to work more like a real-world example.

### Prepare model

There is a delta between existing distributed mnist examples and what's needed to run well as a TFJob. These changes to the [original model](model_original.py) can be viewed in the [included diff](mnist-changes.md)

Basically, we must:

1. Convert the model itself to be importable as a python module, so that the model can be used in other scripts (in this case, [export.py](export.py))
1. Save the graph in a way that's exportable, otherwise you will recieve errors when exporting: `Graph is finalized and cannot be modified.`
1. Add an option to control the training directory, so we can write training results to S3.

The resulting model is [model.py](model.py).

### Prepare distribued Tensorflow components.

The stock distributed Tensorflow [examples](https://github.com/tensorflow/tensorflow/blob/3af03be757b63ea6fbd28cc351d5d2323c526354/tensorflow/tools/dist_test/) expect the cluster spec to be provided via command line arguments. We have modified an [existing shim](https://github.com/kubeflow/kubeflow/blob/d5caf230ff50260c1a6565db35edeeddd5d407e6/tf-controller-examples/tf-cnn/launcher.py) to be more [generic](tf_job_shim.py), and will be using it to wrap our lightly modified examples in order to process TF_CONFIG into something it understands.

### Build and push images.

With our code ready, we will now build/push the docker images

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
docker build . --no-cache  -f Dockerfile.base -t mytfbase:1.0
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_BASE_URL}/mytfmodel:1.0

docker push ${DOCKER_BASE_URL}/mytfmodel:1.0
```

Alternately, you can use this existing image:

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
export S3_ENDPOINT=s3.us-west-2.amazonaws.com
export AWS_ENDPOINT_URL=https://${S3_ENDPOINT}
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
export BUCKET_NAME=mybucket

aws s3api create-bucket --bucket=${BUCKET_NAME}
```

Now upload your training data

```
mc config host add s3 ${AWS_ENDPOINT_URL} ${AWS_ACCESS_KEY_ID} ${AWS_SECRET_ACCESS_KEY}
mc mirror /tmp/mnistdata/ s3/${BUCKET_NAME}/data/mnist/
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, Argo, and Kubernetes Volume Manager to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `tfworkflow`:

### Deploying Tensorflow Operator and Argo.

We are using the Tensorflow operator to automate the deployment of our distributed model training, and Argo to create the overall training pipeline. The easiest way to install these components on your Kubernetes cluster is by using Kubeflow's ksonnet prototypes.

```
NAMESPACE=tfworkflow
APP_NAME=my-kubeflow
ks init ${APP_NAME}
cd ${APP_NAME}

ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow

#TODO pin these to a tag
ks pkg install kubeflow/core@1a6fc9d0e19e456b784ba1c23c03ec47648819d0
ks pkg install kubeflow/argo@8d617d68b707d52a5906d38b235e04e540f2fcf7

# Deploy TF Operator and Argo
kubectl create namespace ${NAMESPACE}
ks generate core kubeflow-core --name=kubeflow-core --namespace=${NAMESPACE}
ks generate argo kubeflow-argo --name=kubeflow-argo --namespace=${NAMESPACE}

ks apply default -c kubeflow-core
ks apply default -c kubeflow-argo

#TODO Add permissions to the argo prototype for tfjobs and other objects.
kubectl apply -f argo-cluster-role.yaml

# Switch context for the rest of the example
kubectl config set-context $(kubectl config current-context) --namespace=${NAMESPACE}
cd -
```

You can check to make sure the components have deployed:

```
$ kubectl logs -l name=tf-job-operator
...
I0226 18:25:16.553804       1 leaderelection.go:184] successfully acquired lease default/tf-operator
I0226 18:25:16.554615       1 controller.go:132] Starting TFJob controller
I0226 18:25:16.554630       1 controller.go:135] Waiting for informer caches to sync
I0226 18:25:16.654781       1 controller.go:140] Starting %v workers1
I0226 18:25:16.654813       1 controller.go:146] Started workers
...

$ kubectl logs -l app=workflow-controller
time="2018-02-26T18:35:48Z" level=info msg="workflow controller configuration from workflow-controller-configmap:\nexecutorImage: argoproj/argoexec:v2.0.0-beta1"
time="2018-02-26T18:35:48Z" level=info msg="Workflow Controller (version: v2.0.0-beta1) starting"
time="2018-02-26T18:35:48Z" level=info msg="Watch Workflow controller config map updates"
time="2018-02-26T18:35:48Z" level=info msg="Detected ConfigMap update. Updating the controller config."
time="2018-02-26T18:35:48Z" level=info msg="workflow controller configuration from workflow-controller-configmap:\nexecutorImage: argoproj/argoexec:v2.0.0-beta1"
time="2018-02-26T18:40:48Z" level=info msg="Alloc=2623 TotalAlloc=45740 Sys=11398 NumGC=20 Goroutines=50"

$ kubectl get crd
NAME                    AGE
tfjobs.kubeflow.org     22m
workflows.argoproj.io   22m

$ argo list
NAME   STATUS   AGE   DURATION
```

### Deploying Kube Volume Controller

Kube Volume Controller is a utility that can seed replicas of datasets across nodes. Think of it as an explicit caching mechanism. In the initial run, KVC downloads the mnist dataset, then in subsquent runs the data is reused, bypassing the download step, and making data available on the local disk.

First we need to install tiller on the cluster with rbac under the kube-system namespace. Instructions can be found [here](https://github.com/kubernetes/helm/blob/ae878f91c36b491b92f046de74784cb462f67419/docs/rbac.md#example-service-account-with-cluster-admin-role) in the section "Example: Service account with cluster-admin role".

Then install Kube Volume Controller:
```
git clone https://github.com/kubeflow/experimental-kvc.git
cd experimental-kvc
git checkout 6a23964
helm install helm-charts/kube-volume-controller/ -n kvc --wait \
  --set clusterrole.install=true \
  --set storageclass.install=true \
  --set tag=6a23964 \
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

The argo workflow can be daunting, but basically our steps above extrapolate as follows:

1. `download-dataset`: Create a `volumemanager` k8s object which is handled by Kube Volume Controller. This will download data to nodes, which can be re-used for subsequent runs to save on download time.
1. `get-workflow-info`: Generate and set variables for consumption in the rest of the pipeline.
1. `tensorboard`: Tensorboard is spawned, configured to watch the S3 URL for the training output.
1. `train-model`: A TFJob is spawned taking in variables such as number of workers, what path the datasets are at, which model container image, etc.
1. `export-model`: The trained model is translated into a servable format.
1. `serve-model`: Optionally, the model is served.

With our workflow defined, we can now execute it.

## Submitting your training workflow

First we need to set a few variables in our workflow. Make sure to set your docker registry or remove the `IMAGE` parameters in order to use our defaults:

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
export S3_DATA_URL=s3://${BUCKET_NAME}/data/mnist/
export S3_TRAIN_BASE_URL=s3://${BUCKET_NAME}/models
export AWS_REGION=us-west-2
export JOB_NAME=myjob-$(uuidgen  | cut -c -5 | tr '[:upper:]' '[:lower:]')
export TF_MODEL_IMAGE=${DOCKER_BASE_URL}/mytfmodel:1.0
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

## Submitting new argo jobs

If you want to rerun your workflow from scratch, then you will need to provide a new `job-name` to the argo workflow. For example:

```
#We're re-using previous variables except JOB_NAME
export JOB_NAME=myawesomejob

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

If you want to test changes to the `volumemanager` object, or want to force a re-download of data, you must delete the existing one:

```
kubectl delete volumemanager mnist
```

## Next Steps

In the future we will be providing tutorials on more advanced examples.

Till then, play with the settings/tunables! And try to use your own model within this workflow.
