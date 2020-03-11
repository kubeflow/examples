# MNIST on Kubeflow

This example guides you through the process of taking an example model, modifying it to run better within Kubeflow, and serving the resulting trained model.

Follow the version of the guide that is specific to how you have deployed Kubeflow

1. [MNIST on Kubeflow on GCP](#gcp)
1. [MNIST on Kubeflow on AWS](#aws)
1. [MNIST on Kubeflow on Azure](#azure)
1. [MNIST on Kubeflow on IBM Cloud](#ibm)
1. [MNIST on Kubeflow on vanilla k8s](#vanilla)

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

<a id=azure></a>
# MNIST on Kubeflow on Azure

Follow these instructions to run the MNIST tutorial on Azure

1. Follow the [Azure instructions](https://www.kubeflow.org/docs/azure/deploy/install-kubeflow/) to deploy Kubeflow on Azure

1. If you do not already have a notebook server, [create a new server](https://www.kubeflow.org/docs/notebooks/setup/)

1. Launch a Jupyter notebook server

   * The tutorial has been tested using the Jupyter Tensorflow 1.15 image

1. Launch a terminal in Jupyter and clone the kubeflow examples repo

   ```
   git clone https://github.com/kubeflow/examples.git git_kubeflow-examples
   ```

   * **Tip** When you start a terminal in Jupyter, run the command `bash` to start
      a bash terminal which is much more friendly then the default shell

   * **Tip** You can change the URL from '/tree' to '/lab' to switch to using Jupyterlab

1. Open the notebook `mnist/mnist_azure.ipynb`

1. Follow the notebook to train and deploy MNIST on Kubeflow

<a id=ibm></a>
# MNIST on Kubeflow on IBM Cloud

Follow these instructions to run the MNIST tutorial on IBM Cloud

1. Follow the [IBM Cloud instructions](https://www.kubeflow.org/docs/ibm/install-kubeflow/) to deploy Kubeflow on IBM Cloud with [IBM Cloud Block Storage](https://www.kubeflow.org/docs/ibm/install-kubeflow/#ibm-cloud-block-storage-setup).

1. Launch a Jupyter notebook

   * The tutorial has been tested using the Jupyter Tensorflow 1.15 and 2.1 image with persistent storage.

1. Launch a terminal in Jupyter and clone the kubeflow examples repo

   ```
   git clone https://github.com/kubeflow/examples.git git_kubeflow-examples
   ```

   * **Tip** When you start a terminal in Jupyter, run the command `bash` to start
      a bash terminal which is much more friendly then the default shell

   * **Tip** You can change the URL from '/tree' to '/lab' to switch to using Jupyterlab

1. Open the notebook `mnist/mnist_ibm.ipynb`

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
