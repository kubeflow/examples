# Reinforcement Learning with [tensorflow/agents](https://github.com/tensorflow/agents)

### WIP

Train a robot arm with reinforcement learning!

Please refer to the [demo notebook](demo/demo.ipynb) for a demonstration of the process of training, monitoring, and rendering.

For clarity and fun you can check out what the product of this tutorial will look like by clicking through the render screenshot below to a short video of a trained agent performing a simulated robotic block grasping task:
[![](demo/render_preview.png)](https://youtu.be/0X0w5XOtcHw)

### Kubeflow and other setup

You can start by authenticating with gcloud in the usual way (i.e. `gcloud auth login` followed by `gcloud config set project <your-project-name>`.

We need to create a Google Cloud Storage bucket to store job logs as well as a unique subdirectory of that bucket to store logs for this particular run. We can create that as follows.

```bash
gsutil mb -p <your-project-name> gs://<your-project-name>
```

Note that you'll need to set the path to this bucket at the beginning of the demo notebook.

TODO: Describe steps to deploy a kubeflow cluster here? Probably just reference what exists elsewhere.

We can pull the credentials for that cluster as follows:

```bash
gcloud container clusters --project={PROJECT} --zone={ZONE} get-credentials {CLUSTER}
```

Next we need to deploy a Kubernetes secret which will provide our the GCP credentials needed to run tensorboard:

TODO: Describe what roles the SA needs to have

```bash
SECRET_FILE_NAME="secret.json"
SECRET_NAME="gcp-credentials"
KEY_FILE="/path/to/your/key.json"
kubectl create -n ${NAMESPACE} secret generic ${SECRET_NAME} \
  --from-file=${SECRET_FILE_NAME}=${KEY_FILE}
```

This example will deploy jobs into the "rl" namespace so let's make sure that exists with the following

```bash
NAMESPACE="rl"
kubectl create namespace ${NAMESPACE}
```

### Running the demo

Now that we have our cluster configured  that you may be interested in configuring your development environment to be able to use the demo notebook.

There are at least two ways this can be done:
1. By running the demonstration container directly (such as on your local machine)
2. By running the demonstration container on a JupyterHub deployment (such as on a remote kubeflow deployment)

#### Direct and local

If running in a Docker container locally you'll need to provide GCP credentials via an environment variable.

TODO

You can run the demonstration container locally using the following

```bash
docker run -p 8888:8888 -it gcr.io/kubeflow-rl/agents-demo:0.1-0209-1106-3869
```

Then opening up the localhost:8888... url printed to STDOUT.

TODO: Will need to have provided GCP credentials as env. var or gcloud auth login from notebook. Discuss alternatives.

#### Remote JupyterHub

To run the examples on a Kubeflow JupyterHub deployment simply provide the examples container name, `gcr.io/kubeflow-rl/agents-demo:0.1-0209-1106-3869`, in the image field of the spawner options dialog, e.g. like so

![](demo/jhub-spawn.png)

TODO: How are credentials obtained when running on jhub?

- Use JupyterLab to upload the service account to your pod
- Set the path to your service account in the cell below and then execute it to activate the service account
- !gcloud auth activate-service-account --key-file={KEY_FILE}
