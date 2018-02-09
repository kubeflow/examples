# Reinforcement Learning with [tensorflow/agents](https://github.com/tensorflow/agents)

### WIP

Train a robot arm with reinforcement learning!

Please refer to the [demo notebook](demo/demo.ipynb) for a demonstration of the process of training, monitoring, and rendering.

For clarity and fun you can check out what the product of this tutorial will look like by clicking through the render screenshot below to a short video of a trained agent performing a simulated robotic block grasping task:
[![](demo/render_preview.png)](https://youtu.be/0X0w5XOtcHw)

### Setup

But before that you may be interested in configuring your development environment to be able to use the demo notebook.

There are at least two ways this can be done:
1. By running the demonstration container directly (such as on your local machine)
2. By running the demonstration container on a JupyterHub deployment (such as on a remote kubeflow deployment)


We need to create a Google Cloud Storage bucket to store job logs as well as a unique subdirectory of that bucket to store logs for this particular run. With the following we first create the GCS bucket then generate the path of a log dir to use in a later step

Set the variables below to a project and bucket suitable for your use.

```bash
#GCP project to use
PROJECT="kubeflow-rl"

# Bucket to use
BUCKET=PROJECT+"-kf"

# K8s cluster to use
CLUSTER="kubeflow-5fc52116"
ZONE="us-east1-d"
NAMESPACE="rl"

# Needed for launching tensorboard
SECRET_NAME = "gcp-credentials"
```

**Attention:** You will need GCP credentials to access the cluster and GCP resources.

If you're running this on your local machine you can authenticate for the GCP project you specified above in the usual way (i.e. `gcloud auth login` followed by `gcloud config set project <your-project-name>`; in this case skip the following step.

If you're running this on JupyterLab you can do the following to provide the right credentials:

- Create a service account with the appropriate roles and download the private key
- Use JupyterLab to upload the service account to your pod
- Set the path to your service account in the cell below and then execute it to activate the service account

Pulling kube credentials
```bash
KEY_FILE="/path/to/your/key.json"
!gcloud auth activate-service-account --key-file={KEY_FILE}
!gsutil mb -p {PROJECT} gs://{BUCKET}

!gcloud container clusters --project={PROJECT} --zone={ZONE} get-credentials {CLUSTER}
!kubectl create namespace {NAMESPACE}
```

Download and install ksonnet if needed

```bash
!if ! [[ $(which ks) ]]; then mkdir -p ${HOME}/bin && curl -L -o ${HOME}/bin/ks "https://github.com/ksonnet/ksonnet/releases/download/v0.8.0/ks-linux-amd64" && chmod a+rx ${HOME}/bin/ks; fi
```

If running on GCP (or possibly another Cloud) you probably need to create a key with credentials to use for your job

```bash
SECRET_FILE_NAME="secret.json"
kubectl create -n {NAMESPACE} secret generic {SECRET_NAME} \
  --from-file={SECRET_FILE_NAME}={KEY_FILE}
```

#### Direct and local



#### Remote JupyterHub
