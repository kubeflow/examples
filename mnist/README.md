<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [MNIST on Kubeflow](#mnist-on-kubeflow)
- [MNIST on Kubeflow on GCP](#mnist-on-kubeflow-on-gcp)
- [MNIST on Kubeflow on AWS](#mnist-on-kubeflow-on-aws)
- [MNIST on Kubeflow on Vanilla k8s](#vanilla)
- [MNIST on other platforms](#mnist-on-other-platforms)
  - [Prerequisites](#prerequisites)
    - [Deploy Kubeflow](#deploy-kubeflow)
    - [Local Setup](#local-setup)
    - [GCP Setup](#gcp-setup)
  - [Modifying existing examples](#modifying-existing-examples)
    - [Prepare model](#prepare-model)
    - [(Optional) Build and push model image.](#optional-build-and-push-model-image)
  - [Preparing your Kubernetes Cluster](#preparing-your-kubernetes-cluster)
    - [Training your model](#training-your-model)
      - [Local storage](#local-storage)
  - [Monitoring](#monitoring)
    - [Tensorboard](#tensorboard)
      - [Local storage](#local-storage-1)
      - [Deploying TensorBoard](#deploying-tensorboard)
  - [Serving the model](#serving-the-model)
    - [Local storage](#local-storage-2)
  - [Web Front End](#web-front-end)
    - [Connecting via port forwarding](#connecting-via-port-forwarding)
  - [Conclusion and Next Steps](#conclusion-and-next-steps)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# MNIST on Kubeflow

This example guides you through the process of taking an example model, modifying it to run better within Kubeflow, and serving the resulting trained model.

Follow the version of the guide that is specific to how you have deployed Kubeflow

1. [MNIST on Kubeflow on GCP](#gcp)
1. [MNIST on Kubeflow on AWS](#aws)
1. [MNIST on Kubeflow on vanilla k8s](#vanilla)
1. [MNIST on other platforms](#other)

<a id=gcp></a>
# MNIST on Kubeflow on GCP

Follow these instructions to run the MNIST tutorial on GCP

1. Follow the [GCP instructions](https://www.kubeflow.org/docs/gke/deploy/) to deploy Kubeflow with IAP

1. Launch a Jupyter notebook

   * The tutorial has been tested using the Jupyter Tensorflow 1.15 image

1. Launch a terminal in Jupyter and clone the kubeflow examples repo

   ```
   git clone https://github.com/kubeflow/examples.git git_kubeflow-examples
   ```

   * **Tip** When you start a terminal in Jupyter, run the command `bash` to start
      a bash terminal which is much more friendly then the default shell

   * **Tip** You can change the URL from '/tree' to '/lab' to switch to using Jupyterlab

1. Open the notebook `mnist/mnist_gcp.ipynb`

1. Follow the notebook to train and deploy MNIST on Kubeflow

<a id=aws></a>
# MNIST on Kubeflow on AWS

Follow these instructions to run the MNIST tutorial on AWS

1. Follow the [AWS instructions](https://www.kubeflow.org/docs/aws/deploy/install-kubeflow/) to deploy Kubeflow on AWS

1. Launch a Jupyter notebook

   * The tutorial has been tested using the Jupyter Tensorflow 1.15 image

1. Launch a terminal in Jupyter and clone the kubeflow examples repo

   ```
   git clone https://github.com/kubeflow/examples.git git_kubeflow-examples
   ```

   * **Tip** When you start a terminal in Jupyter, run the command `bash` to start
      a bash terminal which is much more friendly then the default shell

   * **Tip** You can change the URL from '/tree' to '/lab' to switch to using Jupyterlab

1. Open the notebook `mnist/mnist_aws.ipynb`

1. Follow the notebook to train and deploy MNIST on Kubeflow

<a id=vanilla></a>
# MNIST on Kubeflow on Vanilla k8s

1. Follow these [instructions](https://www.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/) to deploy Kubeflow.

1. [Setup docker credentials](#vanilla-docker).

1. Launch a Jupyter Notebook

  * The tutorial is run on Jupyter Tensorflow 1.15 image.

1. Launch a terminal in Jupyter and clone the kubeflow/examples repo

  ```bash
  git clone https://github.com/kubeflow/examples.git git_kubeflow-examples
  ```

1. Open the notebook `mnist/mnist_vanilla_k8s.ipynb`

1. Follow the notebook to train and deploy on MNIST on Kubeflow

<a id=vanilla-docker></a>
### Prerequisites

### Configure docker credentials

#### Why do we need this?

Kaniko is used by fairing to build the model every time the notebook is run and deploy a fresh model.
The newly built image is pushed into the DOCKER_REGISTRY and pulled from there by subsequent resources.

Get your docker registry user and password encoded in base64 <br>

`echo -n USER:PASSWORD | base64` <br>

Create a config.json file with your Docker registry url and the previous generated base64 string <br>
```json
{
	"auths": {
		"https://index.docker.io/v1/": {
			"auth": "xxxxxxxxxxxxxxx"
		}
	}
}
```

<br>

### Create a config-map in the namespace you're using with the docker config

`kubectl create --namespace ${NAMESPACE} configmap docker-config --from-file=<path to config.json>`

Source documentation: [Kaniko docs](https://github.com/GoogleContainerTools/kaniko#pushing-to-docker-hub)

<a id=other></a>
# MNIST on other platforms

The tutorial is currently not up to date for Kubeflow 1.0. Please check the issues

* [kubeflow/examples#725](https://github.com/kubeflow/examples/issues/725) for other platforms

## Prerequisites

Before we get started there are a few requirements.

### Deploy Kubeflow

Follow the [Getting Started Guide](https://www.kubeflow.org/docs/started/getting-started/) to deploy Kubeflow.

### Local Setup

You also need the following command line tools:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [kustomize](https://kustomize.io/)

**Note:** kustomize [v2.0.3](https://github.com/kubernetes-sigs/kustomize/releases/tag/v2.0.3) is recommented since the [problem](https://github.com/kubernetes-sigs/kustomize/issues/1295) in kustomize v2.1.0.

### GCP Setup

If you are using GCP, need to enable [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) to execute below steps.

## Modifying existing examples

Many examples online use models that are unconfigurable, or don't work well in distributed mode. We will modify one of these [examples](https://github.com/tensorflow/tensorflow/blob/9a24e8acfcd8c9046e1abaac9dbf5e146186f4c2/tensorflow/examples/learn/mnist.py) to be better suited for distributed training and model serving.

### Prepare model

There is a delta between existing distributed mnist examples and what's needed to run well as a TFJob.

Basically, we must:

1. Add options in order to make the model configurable.
1. Use `tf.estimator.train_and_evaluate` to enable model exporting and serving.
1. Define serving signatures for model serving.

The resulting model is [model.py](model.py).

### (Optional) Build and push model image.

With our code ready, we will now build/push the docker image, or use the existing image `gcr.io/kubeflow-ci/mnist/model:latest` without building and pushing.

```
DOCKER_URL=docker.io/reponame/mytfmodel:tag # Put your docker registry here
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_URL}

docker push ${DOCKER_URL}
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, and Argo to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `kubeflow`.

```
kubectl config set-context $(kubectl config current-context) --namespace=kubeflow
```

### Training your model

#### Local storage

Let's start by runing the training job on Kubeflow and storing the model in a local storage.

Fristly, refer to the [document](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) to create Persistent Volume(PV) and Persistent Volume Claim(PVC), the PVC name (${PVC_NAME}) will be used by pods of training and serving for local mode in steps below.

Enter the `training/local` from the `mnist` application directory.
```
cd training/local
```

Give the job a name to indicate it is running locally

```
kustomize edit add configmap mnist-map-training --from-literal=name=mnist-train-local
```

Point the job at your custom training image

```
kustomize edit set image training-image=$DOCKER_URL
```

Optionally, configure it to run distributed by setting the number of parameter servers and workers to use. The `numPs` means the number of Ps and the `numWorkers` means the number of Worker.

```
../base/definition.sh --numPs 1 --numWorkers 2
```

Set the training parameters, such as training steps, batch size and learning rate.

```
kustomize edit add configmap mnist-map-training --from-literal=trainSteps=200
kustomize edit add configmap mnist-map-training --from-literal=batchSize=100
kustomize edit add configmap mnist-map-training --from-literal=learningRate=0.01
```

To store the the exported model and checkpoints model, configure PVC name and mount piont.

```
kustomize edit add configmap mnist-map-training --from-literal=pvcName=${PVC_NAME}
kustomize edit add configmap mnist-map-training --from-literal=pvcMountPath=/mnt
```

Now we need to configure parameters and telling the code to save the model to PVC.

```
kustomize edit add configmap mnist-map-training --from-literal=modelDir=/mnt
kustomize edit add configmap mnist-map-training --from-literal=exportDir=/mnt/export
```

You can now submit the job

```
kustomize build . |kubectl apply -f -
```

And you can check the job

```
kubectl get tfjobs -o yaml mnist-train-local
```

And to check the logs

```
kubectl logs mnist-train-local-chief-0
```

## Monitoring

There are various ways to monitor workflow/training job. In addition to using `kubectl` to query for the status of `pods`, some basic dashboards are also available.

### Tensorboard

#### Local storage

Enter the `monitoring/local` from the `mnist` application directory.
```
cd monitoring/local
```

Configure PVC name, mount point, and set log directory.
```
kustomize edit add configmap mnist-map-monitoring --from-literal=pvcName=${PVC_NAME}
kustomize edit add configmap mnist-map-monitoring --from-literal=pvcMountPath=/mnt
kustomize edit add configmap mnist-map-monitoring --from-literal=logDir=/mnt
```

#### Deploying TensorBoard

Now you can deploy TensorBoard

```
kustomize build . | kubectl apply -f -
```

To access TensorBoard using port-forwarding

```
kubectl port-forward service/tensorboard-tb 8090:80
```
TensorBoard can now be accessed at [http://127.0.0.1:8090](http://127.0.0.1:8090).

## Serving the model

The model code will export the model in saved model format which is suitable for serving with TensorFlow serving.

To serve the model follow the instructions below. The instructins vary slightly based on where you are storing your model (e.g. GCS, S3, PVC). Depending on the storage system we provide different kustomization as a convenience for setting relevant environment variables.


### Local storage

The section shows how to serve the local model that was stored in PVC while training.

Enter the `serving/local` from the `mnist` application directory.

```
cd serving/local
```

Set a different name for the tf-serving.

```
kustomize edit add configmap mnist-map-serving --from-literal=name=mnist-service-local
```

Mount the PVC, by default the pvc will be mounted to the `/mnt` of the pod.

```
kustomize edit add configmap mnist-map-serving --from-literal=pvcName=${PVC_NAME}
kustomize edit add configmap mnist-map-serving --from-literal=pvcMountPath=/mnt
```

Configure a filepath for the exported model.

```
kustomize edit add configmap mnist-map-serving --from-literal=modelBasePath=/mnt/export
```

Deploy it, and run a service to make the deployment accessible to other pods in the cluster.

```
kustomize build . |kubectl apply -f -
```

You can check the deployment by running
```
kubectl describe deployments mnist-service-local
```

The service should make the `mnist-service-local` deployment accessible over port 9000.
```
kubectl describe service mnist-service-local
```

## Web Front End

The example comes with a simple web front end that can be used with your model.

Enter the `front` from the `mnist` application directory.

```
cd front
```

To deploy the web front end

```
kustomize build . |kubectl apply -f -
```

### Connecting via port forwarding

To connect to the web app via port-forwarding

```
POD_NAME=$(kubectl get pods --selector=app=web-ui --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')

kubectl port-forward ${POD_NAME} 8080:5000
```

You should now be able to open up the web app at your localhost. [Local Storage](http://localhost:8080) or [S3](http://localhost:8080/?addr=mnist-s3-serving).

## Conclusion and Next Steps

This is an example of what your machine learning can look like. Feel free to play with the tunables and see if you can increase your model's accuracy (increasing `model-train-steps` can go a long way).
