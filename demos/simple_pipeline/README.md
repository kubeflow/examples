# Kubeflow demo - Simple pipeline

This repository contains a demonstration of Kubeflow capabilities, suitable for
presentation to public audiences.

The base demo includes the following steps:

1. [Setup your environment](#1-setup-your-environment)
1. [Install kubeflow on GKE](#2-install-kubeflow-on-gke)
1. [Install pipelines on GKE](#3-install-pipelines-on-gke)
1. [Run a simple pipeline](#4-run-a-simple-pipeline)

## 1. Setup your environment

Set environment variables by sourcing the env file:

```
. kubeflow-demo-simple-pipeline.env
```

Create a clean pipeline environment:

```
conda create --name kfp python=3.6
source activate kfp
```

Install the Kubeflow pipeline SDK:

```
pip install https://storage.googleapis.com/ml-pipeline/kfp-0.0.23.tar.gz --upgrade
```

### Create a GKE cluster

```
kfctl init ${CLUSTER} --platform gcp
cd ${CLUSTER}
kfctl generate platform
kfctl apply platform
```

## 2. Install kubeflow on GKE

```
kfctl generate k8s
kfctl apply k8s
```

## 3. Install pipelines on GKE

```
cd ks_app
ks registry add ml-pipeline "${PIPELINES_REPO}/ml-pipeline"
ks pkg install ml-pipeline/ml-pipeline
ks generate ml-pipeline ml-pipeline
ks param set ml-pipeline namespace kubeflow
ks apply default -c ml-pipeline
```

View the installed components in the GCP Console. In the
[Kubernetes Engine](https://console.cloud.google.com/kubernetes)
section, you will see a new cluster ${CLUSTER}. Under
[Workloads](https://console.cloud.google.com/kubernetes/workload),
you will see all the default Kubeflow and pipeline components.

## 4. Run a simple pipeline

Show the file `sequential.py` as an example of a simple pipeline.

Compile it to create a .tar.gz file:

```
./sequential.py
```

Unzip the file to reveal `pipeline.yaml`.

```
tar -xvf sequential.py.tar.gz
```

Connect to the pod:

```
kubectl port-forward ml-pipeline-ui-cd976567-x64qn 8080:3000
```

In the browser, navigate to `localhost:8080` and create a new pipeline by
uploading `pipeline.yaml`. Use the url `gs://ml-pipeline/shakespeare1.txt` as an
input parameter.

Select the pipeline and click "Create job." Select "Jobs" from the left-hand
side, then "Runs". Click on the job to view the graph. Select the final step to
view results.

