# Reinforcement Learning with [tensorflow/agents](https://github.com/tensorflow/agents)

Train a robot arm with reinforcement learning!

Please refer to the [demo notebook](demo/demo.ipynb) for a demonstration of the process of training, monitoring, and rendering.

To get your local or remote system configured to run the demo see the setup instructions below.

For clarity and fun you can check out what the product of this tutorial will look like by clicking through the render screenshot below to a short video of a trained agent performing a simulated robotic block grasping task:

[![](demo/render_preview.png)](https://youtu.be/0X0w5XOtcHw)

### Setup

##### GCP and Kubeflow configuration

Credentials are needed in order to make the calls to the Google Cloud platform APIs dispatched in subsequent steps. You can start by authenticating with GCloud in the usual way (i.e. `gcloud auth login` followed by `gcloud config set project <your-project-name>`).

First, we need to create a Google Cloud Storage bucket to store job logs as well as a unique subdirectory of that bucket to store logs for this particular run. We can create that as follows:

```bash
gsutil mb -p <your-project-name> gs://<your-project-name>
```

Note that you'll need to set the path to this bucket at the beginning of the [demo notebook](demo/demo.ipynb) so remember it for later!

This tutorial assumes you have already deployed kubeflow on a Kubernetes cluster running on Google Cloud Platform. Check out [these](https://cloud.google.com/kubernetes-engine/docs/quickstart) [instructions](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) if you haven't already done so.

We can pull the credentials for that cluster as follows:

```bash
gcloud container clusters --project={PROJECT} \
  --zone={ZONE} get-credentials {CLUSTER}
```

Next we need to deploy a Kubernetes secret which will provide the GCP credentials needed to run TensorBoard:

```bash
SECRET_FILE_NAME="secret.json"
SECRET_NAME="gcp-credentials"
KEY_FILE="/path/to/your/key.json"
kubectl create -n ${NAMESPACE} secret generic ${SECRET_NAME} \
  --from-file=${SECRET_FILE_NAME}=${KEY_FILE}
```

This service account key will need read access to Google Cloud Storage in order to permit TensorBoard to read training log data that it will then display in the TensorBoard UI.

Lastly, this example will deploy jobs into the "rl" namespace so let's make sure that exists with the following:

```bash
NAMESPACE="rl"
kubectl create namespace ${NAMESPACE}
```

##### Ksonnet setup

Ksonnet is a tool to simplify configuration management for kubernetes deployments which extends to making it easier to specify and re-configure distributed neural network training jobs on Kubeflow.

Before we can use it we need to do a little setup of our local machine namely registering a particular kubernetes cluster as the default for Ksonnet and pulling the Kubeflow Ksonnet libraries that are needed in order to use Ksonnet to manage Kubeflow training jobs.

These setup steps are automated and you can run them with the following command:

```bash
sh setup.sh
```

### Running the demo

As mentioned above this example demonstrates the training of a reinforcement learning agent in performing a robotic control task. There are two aspects to discuss:
1. The docker image the encapsulates all that is needed to define the training task, and
2. The Jupyter Notebook container that is sufficient to view the demonstration notebook and dispatch training jobs that utilize the preceeding.

#### Job container

If you're only interested in running this example and examining the intermediate and final outputs you don't necessarily need to re-build the container that encapsulates the training task. A public version of this container can be found here:

If you look ahead to the demonstration notebook you'll see we specify the address of this container when parameterizing our training job.

Alternatively, especially in the case where you want to make modifications to the example, you may want to re-build the training container image. This can be done by running

```bash
sh build.sh
```

Once built the image needs to be made available on a container registry accessible to the kubeflow deployment that will be pulling and running it. If your Kubernetes cluster is running on the Google Cloud Platform then a good pattern is to push your image to a Google Container Registry (GCR) that is either
1. Owned by the same project as your GKE cluster, or
2. Public

You can push your recent container build to GCR with the following command:

```bash
gcloud docker -- push ${IMAGE_TAG}
```

#### Demonstration notebook

There are two ways you can run the demonstration notebook.

###### Jupyter on host OS

The demo notebook can be run using a traditional Jupyter Notebook server (i.e. one launched via the `jupyter notebook` command in your favorite command-line shell environment 🤓).

To start a Jupyter Notebook server running on your local machine simply run the command `jupyter notebook` from a path on your filesystem that is parent (perhaps even great grand-) to the path of the demo notebook. Then simply open the notebook and run the commands! Actually there are a few essentials, namely that the environment in which the notebook was launched has
1. Ksonnet configured and accessible via the `ks` command, and
2. The `gcloud` command is available, authenticated, and configured to the correct project,

###### Jupyter in Docker

Often it's more convenient just to pull a docker container that already has all of the necessary dependencies installed (namely the gcloud and ksonnet, jupyter, tensorflow, and various other python dependencies). The modest complication in this case is that in contrast to the above where `gcloud auth login` was sufficient to authenticate the `gcloud` command line tool to make requests to your GCP project of interest - in the case where these API requests are being made from inside a container that container needs to be authenticated using the service account pattern.

We can accomplish this by obtaining then mounting a service account key into the directory space of the container. Steps are provided in the demo notebook describing how to activate these credentials so let's talk about how to provide them to the container in that way.

You'll notice with the following the argument -v [source]:[target] allows us to mount a local filesystem path to a target path in a docker container run. In the following simply replace </local/path/to/sa.json> with the local filesystem path to your service account key:

```bash
DEMO_NOTEBOOK_IMAGE=gcr.io/kubeflow-rl/agents-demo:0.1-0209-1216-b7fd
docker run -p 8888:8888 \
  -v </local/path/to/sa.json>:/home/jovyan/sa.json \
  -it ${DEMO_NOTEBOOK_IMAGE}
```

e.g. you would use "-v /tmp/mykey.json:/home/jovyan/sa.json" if the key were on your local filesystem at /tmp/mykey.json.

The above will produce output that includes at the end a URL along with an access key parameter which you can copy and pase into a browser of your choice and the demo notebook will be available in a subdirectory that maps to the demo subdirectory of the root directory of this example.

One gotcha to mention is that if you already have jupyter or some other process occupying port 8888 on your localhost that will continue to take precedence over that port instead of your containerized jupyter process. The workaround for this is to clear up 8888 on localhost or map 8888 in the container to some other port localhost (e.g. 12347).

###### JupyterHub

To run the examples on a Kubeflow JupyterHub deployment simply provide the examples container name, `gcr.io/kubeflow-rl/agents-demo:0.1-0209-1216-b7fd`, in the image field of the spawner options dialog. Here's what that looks like for me:

![](demo/jhub-spawn.png)

Once you've accessed your Jupyter server you can upload service account credentials from your local machine to the JH instance via Jupyter's file upload dialog. This will by default place them at /home/joyvan/[your-key].json which you'll use in the first step of the demonstration which involves activating the service account credentials.

Well our time getting things set up was fun but it's time now to move on to better things namely playing around that shiny new demonstration notebook!
