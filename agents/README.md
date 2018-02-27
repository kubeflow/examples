# Reinforcement Learning with [tensorflow/agents](https://github.com/tensorflow/agents)

[![Docker Repository on Quay](https://quay.io/repository/cwbeitel/agents-demo/status "Docker Repository on Quay")](https://quay.io/repository/cwbeitel/agents-demo)

Here we provide a demonstration of training a reinforcement learning agent to perform a robotic grasping task using Kubeflow running on Google Kubernetes Engine. In this demonstration you will learn how to paramaeterize a training job, submit it to run on your cluster, monitor the job including launching a tensorboard instance, and finally producing renders of the agent performing the robotic grasping task.

For clarity and fun you can check out what the product of this tutorial will look like by clicking through the render screenshot below to a short video of a trained agent performing a simulated robotic block grasping task:

[![](doc/render_preview.png)](https://youtu.be/0X0w5XOtcHw)

Below are instructions to first set up various preliminaries then launch the example notebook in a variety of forms.

### Setup

##### GCP and Kubeflow configuration

This tutorial assumes you have deployed a Kubernetes cluster on your provider of choice and have completed the steps described in the [Kubeflow User Guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) to deploy the core, argo, and nfs components.

Beyond that setup is minimal simply requiring that we have created a namespace to encapsulate our training jobs (as is a best practice but not required) as follows:

```bash
NAMESPACE="rl"
kubectl create namespace ${NAMESPACE}
```

Note the above command assumes you have already pulled the credentials for your Kubernetes cluster locally as described in the [Kubeflow User Guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md).

### Running the demo on JupyterHub

In order to run this demo on a Kubeflow JupyterHub deployment you'll need the registry address of a demo container that is accessible to that Kubeflow deployment. This can be accomplished using the public container image for this demo, `quay.io/cwbeitel/agents-demo`, or by building the demo container yourself.

Please refer to [these docs](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) for accessing your JupyterHub deployment.

##### Launching

To run the examples on a Kubeflow JupyterHub deployment simply provide the registry address of your demonstration container, e.g. `quay.io/cwbeitel/agents-demo`, in the image field of the spawner options dialog.

Here's approximately what that looks like for me:

![](doc/jhub-spawn.png)

For troubleshooting of your JupyterHub spawn or anything else related to your Kubeflow deployment please refer to the [Kubeflow User Guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md).

Well it looks like our initial setup is finished 🎉🎉 and it's time to start playing around with that shiny new demonstration notebook!!

##### Building your own development container

We might want to include various additional dependencies in our notebook container to aid in development of our model. In that case we might be interested in modifying the demo Dockerfile and re-building the container.

The demo container can be built using the standard workflow:

```bash
TAG=quay.io/someuser/agents-demo:version
docker build -t ${TAG} .
docker push ${TAG}
```
