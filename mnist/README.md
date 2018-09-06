# Training MNIST using Kubeflow, S3, and Argo.

This example guides you through the process of taking an example model, modifying it to run better within Kubeflow, and serving the resulting trained model. We will be using Argo to manage the workflow, Tensorflow's S3 support for saving model training info, Tensorboard to visualize the training, and Kubeflow to deploy the Tensorflow operator and serve the model.

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
gcloud alpha container clusters create ${USER} --enable-kubernetes-alpha --machine-type=n1-standard-8 --num-nodes=3 --disk-size=200 --zone=us-west1-a --cluster-version=1.9.3-gke.0 --image-type=UBUNTU
```

If using Azure, the following will provision a cluster with the required features, [using the az cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest):

```
# Create a resource group
az group create -n kubeflowrg -l eastus
# Deploy the cluster
az aks create -n kubeflowaks -g kubeflowrg -l eastus -k 1.9.6 -c 3 -s Standard_NC6
# Authentication into the cluster
az aks get-credentials -n kubeflowaks -g kubeflowrg
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
- [ksonnet](https://ksonnet.io/#get-started)

To run the client at the end of the example, you must have [requirements.txt](requirements.txt) intalled in your active python environment.

```
pip install -r requirements.txt
```

NOTE: These instructions rely on Github, and may cause issues if behind a firewall with many Github users. Make sure you [generate and export this token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/):

```
export GITHUB_TOKEN=xxxxxxxx
```

## Modifying existing examples

Many examples online use models that are unconfigurable, or don't work well in distributed mode. We will modify one of these [examples](https://github.com/tensorflow/tensorflow/blob/9a24e8acfcd8c9046e1abaac9dbf5e146186f4c2/tensorflow/examples/learn/mnist.py) to be better suited for distributed training and model serving.

### Prepare model

There is a delta between existing distributed mnist examples and what's needed to run well as a TFJob.

Basically, we must:

1. Add options in order to make the model configurable.
1. Use `tf.estimator.train_and_evaluate` to enable model exporting and serving.
1. Define serving signatures for model serving.

The resulting model is [model.py](model.py).

### Build and push model image.

With our code ready, we will now build/push the docker image.

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_BASE_URL}/mytfmodel:1.7

docker push ${DOCKER_BASE_URL}/mytfmodel:1.7
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, and Argo to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `tfworkflow`:

### Deploying Tensorflow Operator and Argo.

We are using the Tensorflow operator to automate the deployment of our distributed model training, and Argo to create the overall training pipeline. The easiest way to install these components on your Kubernetes cluster is by using Kubeflow's ksonnet prototypes.

```
NAMESPACE=tfworkflow
APP_NAME=my-kubeflow
ks init ${APP_NAME}
cd ${APP_NAME}

ks registry add kubeflow github.com/kubeflow/kubeflow/tree/v0.2.4/kubeflow

ks pkg install kubeflow/core@v0.2.4
ks pkg install kubeflow/argo

# Deploy TF Operator and Argo
kubectl create namespace ${NAMESPACE}
ks generate core kubeflow-core --name=kubeflow-core --namespace=${NAMESPACE}
ks generate argo kubeflow-argo --name=kubeflow-argo --namespace=${NAMESPACE}

ks apply default -c kubeflow-core
ks apply default -c kubeflow-argo

# Switch context for the rest of the example
kubectl config set-context $(kubectl config current-context) --namespace=${NAMESPACE}
cd -

# Create a user for our workflow
kubectl apply -f tf-user.yaml
```

You can check to make sure the components have deployed:

```
$ kubectl get pods -l name=tf-job-operator
NAME                              READY     STATUS    RESTARTS   AGE
tf-job-operator-78757955b-2glvj   1/1       Running   0          1m

$ kubectl get pods -l app=workflow-controller
NAME                                   READY     STATUS    RESTARTS   AGE
workflow-controller-7d8f4bc5df-4zltg   1/1       Running   0          1m

$ kubectl get crd
NAME                    AGE
tfjobs.kubeflow.org     1m
workflows.argoproj.io   1m

$ argo list
NAME   STATUS   AGE   DURATION
```

### Creating secrets for our workflow and setting S3 variables.

For fetching and uploading data, our workflow requires S3 credentials and variables. These credentials will be provided as kubernetes secrets, and the variables will be passed into the workflow. Modify the below values to suit your environment.

```
export S3_ENDPOINT=s3.us-west-2.amazonaws.com  #replace with your s3 endpoint in a host:port format, e.g. minio:9000
export AWS_ENDPOINT_URL=https://${S3_ENDPOINT} #use http instead of https for default minio installs
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
export AWS_REGION=us-west-2
export BUCKET_NAME=mybucket
export S3_USE_HTTPS=1 #set to 0 for default minio installs
export S3_VERIFY_SSL=1 #set to 0 for defaul minio installs

kubectl create secret generic aws-creds --from-literal=awsAccessKeyID=${AWS_ACCESS_KEY_ID} \
 --from-literal=awsSecretAccessKey=${AWS_SECRET_ACCESS_KEY}
```

## Defining your training workflow

This is the bulk of the work, let's walk through what is needed:

1. Train the model
1. Export the model
1. Serve the model

Now let's look at how this is represented in our [example workflow](model-train.yaml)

The argo workflow can be daunting, but basically our steps above extrapolate as follows:

1. `get-workflow-info`: Generate and set variables for consumption in the rest of the pipeline.
1. `tensorboard`: Tensorboard is spawned, configured to watch the S3 URL for the training output.
1. `train-model`: A TFJob is spawned taking in variables such as number of workers, what path the datasets are at, which model container image, etc. The model is exported at the end.
1. `serve-model`: Optionally, the model is served.

With our workflow defined, we can now execute it.

## Submitting your training workflow

First we need to set a few variables in our workflow. Make sure to set your docker registry or remove the `IMAGE` parameters in order to use our defaults:

```
DOCKER_BASE_URL=docker.io/elsonrodriguez # Put your docker registry here
export S3_DATA_URL=s3://${BUCKET_NAME}/data/mnist/
export S3_TRAIN_BASE_URL=s3://${BUCKET_NAME}/models
export JOB_NAME=myjob-$(uuidgen  | cut -c -5 | tr '[:upper:]' '[:lower:]')
export TF_MODEL_IMAGE=${DOCKER_BASE_URL}/mytfmodel:1.7
export TF_WORKER=3
export MODEL_TRAIN_STEPS=200
```

Next, submit your workflow.

```
argo submit model-train.yaml -n ${NAMESPACE} --serviceaccount tf-user \
    -p aws-endpoint-url=${AWS_ENDPOINT_URL} \
    -p s3-endpoint=${S3_ENDPOINT} \
    -p aws-region=${AWS_REGION} \
    -p tf-model-image=${TF_MODEL_IMAGE} \
    -p s3-data-url=${S3_DATA_URL} \
    -p s3-train-base-url=${S3_TRAIN_BASE_URL} \
    -p job-name=${JOB_NAME} \
    -p tf-worker=${TF_WORKER} \
    -p model-train-steps=${MODEL_TRAIN_STEPS} \
    -p s3-use-https=${S3_USE_HTTPS} \
    -p s3-verify-ssl=${S3_VERIFY_SSL} \
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

There are various ways to monitor workflow/training job. In addition to using `kubectl` to query for the status of `pods`, some basic dashboards are also available.

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

```
POD_NAME=$(kubectl get pod -l=app=mnist-${JOB_NAME} -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward ${POD_NAME} 9000:9000 &
TF_MNIST_IMAGE_PATH=data/7.png python mnist_client.py
```

This should result in output similar to this, depending on how well your model was trained:
```
outputs {
  key: "classes"
  value {
    dtype: DT_UINT8
    tensor_shape {
      dim {
        size: 1
      }
    }
    int_val: 7
  }
}
outputs {
  key: "predictions"
  value {
    dtype: DT_FLOAT
    tensor_shape {
      dim {
        size: 1
      }
      dim {
        size: 10
      }
    }
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 1.0
    float_val: 0.0
    float_val: 0.0
  }
}


............................
............................
............................
............................
............................
............................
............................
..............@@@@@@........
..........@@@@@@@@@@........
........@@@@@@@@@@@@........
........@@@@@@@@.@@@........
........@@@@....@@@@........
................@@@@........
...............@@@@.........
...............@@@@.........
...............@@@..........
..............@@@@..........
..............@@@...........
.............@@@@...........
.............@@@............
............@@@@............
............@@@.............
............@@@.............
...........@@@..............
..........@@@@..............
..........@@@@..............
..........@@................
............................
Your model says the above number is... 7!
```

You can also omit `TF_MNIST_IMAGE_PATH`, and the client will pick a random number from the mnist test data. Run it repeatedly and see how your model fares!

### Disabling Serving

Model serving can be turned off by passing in `-p model-serving=false` to the `model-train.yaml` workflow. Then if you wish to serve your model after training, use the `model-deploy.yaml` workflow. Simply pass in the desired finished argo workflow as an argument:

```
WORKFLOW=<the workflowname>
argo submit model-deploy.yaml -n ${NAMESPACE} -p workflow=${WORKFLOW} --serviceaccount=tf-user
```

## Submitting new argo jobs

If you want to rerun your workflow from scratch, then you will need to provide a new `job-name` to the argo workflow. For example:

```
#We're re-using previous variables except JOB_NAME
export JOB_NAME=myawesomejob

argo submit model-train.yaml -n ${NAMESPACE} --serviceaccount tf-user \
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

## Conclusion and Next Steps

This is an example of what your machine learning pipeline can look like. Feel free to play with the tunables and see if you can increase your model's accuracy (increasing `model-train-steps` can go a long way).
