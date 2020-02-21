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
