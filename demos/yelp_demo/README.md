# Kubeflow demo - Yelp restaurant reviews

This repository contains a demonstration of Kubeflow capabilities, suitable for
presentation to public audiences.

The base demo includes the following steps:

1. [Install kubeflow locally](#1-install-kubeflow-locally)
1. [Bring up a notebook](#2-bring-up-a-notebook)
1. [Run training locally](#3-run-training-locally)
1. [Install kubeflow on GKE](#4-install-kubeflow-on-gke)
1. [Run training on GKE](#5-run-training-on-gke)
1. [Create the serving and UI components](#6-create-the-serving-and-ui-components)

## Important! Pre-work

Before completing any of the below steps, follow the instructions in [./demo_setup](./demo_setup/README.md) to prepare for demonstrating Kubeflow.

## 1. Install kubeflow locally

Initialize a ksonnet app:

```
ks init kubeflow
cd kubeflow
```

Install packages and generate core components:

```
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow
ks pkg install kubeflow/core@${VERSION}
ks pkg install kubeflow/tf-serving@${VERSION}
ks pkg install kubeflow/tf-job@${VERSION}
ks generate core kubeflow-core --name=kubeflow-core
```

Create the minikube environment and set the cloud parameter:

```
ks env add minikube --namespace=${NAMESPACE}
ks param set --env minikube kubeflow-core \
  cloud "minikube"
```

Apply kubeflow to the cluster:

```
ks apply minikube -c kubeflow-core
```

## 2. Bring up a notebook

Connect to Jupyterhub by forwarding a port and opening a browser to
[localhost:8000](localhost:8000):

```
kubectl port-forward tf-hub-0 8000:8000
```

Spawn a new pod with this image:

```
gcr.io/kubeflow-dev/issue-summarization-notebook-cpu:latest
```

Once the notebook environment is
available, open a new terminal and upload this [Simple ML Model
notebook](notebooks/simple_ml_model.ipynb).

Execute the notebook to show that it works.

## 3. Run training locally

Retrieve the following files for the t2tcpu & t2ttpu jobs:

```
cp ${REPO_PATH}/demo/components/t2t[ct]pu.* components
cp ${REPO_PATH}/demo/components/params.* components
```

Set parameter values for training:

```
ks param set --env minikube t2tcpu \
  cloud "minikube"
ks param set --env minikube t2tcpu \
  dataDir ${GCS_TRAINING_DATA_DIR}
ks param set --env minikube t2tcpu \
  outputGCSPath ${GCS_TRAINING_OUTPUT_DIR_LOCAL}
ks param set --env minikube t2tcpu \
  cpuImage gcr.io/${DEMO_PROJECT}/kubeflow-yelp-demo-cpu:latest
ks param set --env minikube t2tcpu \
  workers 2
```

Generate manifests and apply to cluster:

```
ks apply minikube -c t2tcpu
```

## 4. Install kubeflow on GKE

Switch to a GKE cluster:

```
kubectl config use-context gke
```

Create an environment:

```
ks env add gke --namespace=${NAMESPACE}
```

Set parameter values for kubeflow-core:

```
ks param set --env gke kubeflow-core \
  cloud "gke"
```

Install kubeflow on the cluster:

```
ks apply gke -c kubeflow-core
```

## 5. Run training on GKE

### Distributed CPU training

Set parameter values for training:

```
ks param set --env gke t2tcpu \
  dataDir ${GCS_TRAINING_DATA_DIR}
ks param set --env gke t2tcpu \
  outputGCSPath ${GCS_TRAINING_OUTPUT_DIR_CPU}
```

Warning: this command can take hours(!) to complete if the number of steps is
above 1000.

```
ks apply gke -c t2tcpu
```

#### Export the trained model

This will export the model to an `export/` directory in output_dir.

```
cd ../yelp
t2t-exporter \
  --t2t_usr_dir=${USR_DIR} \
  --model=${MODEL} \
  --hparams_set=${HPARAMS_SET} \
  --problem=${PROBLEM} \
  --data_dir=${GCS_TRAINING_DATA_DIR} \
  --output_dir=${GCS_TRAINING_OUTPUT_DIR_CPU}
```

### Distributed TPU training

Set parameter values for training:

```
ks param set --env gke t2ttpu \
  dataDir ${GCS_TRAINING_DATA_DIR}
ks param set --env gke t2ttpu \
  outputGCSPath ${GCS_TRAINING_OUTPUT_DIR_TPU}
```

Warning: this command can take hours(!) to complete if the number of steps is
above 1000.

```
ks apply gke -c t2ttpu
```

#### Export the trained model

This will export the model to an `export/` directory in output_dir.

```
cd ../yelp
t2t-exporter \
  --t2t_usr_dir=${USR_DIR} \
  --model=${MODEL} \
  --hparams_set=${HPARAMS_SET} \
  --problem=${PROBLEM} \
  --data_dir=${GCS_TRAINING_DATA_DIR} \
  --output_dir=${GCS_TRAINING_OUTPUT_DIR_TPU}
```

## 6. Create the serving and UI components

Retrieve the following files for the serving & UI components:

```
cp ${REPO_PATH}/demo/components/serving.* components
cp ${REPO_PATH}/demo/components/ui.* components
```


Set parameter values for serving:

```
ks param set --env gke serving \
  modelPath ${GCS_TRAINING_OUTPUT_DIR_TPU}/export/Servo
```

Create the serving and UI components:

```
ks apply gke -c serving -c ui
```

Forward the port for viewing from a local browser:
```
UI_POD=$(kubectl get po -l app=kubeflow-demo-ui | \
  grep kubeflow-demo-ui | \
  head -n 1 | \
  cut -d " " -f 1 \
)
kubectl port-forward ${UI_POD} 8080:80
```

Optional: Setup an SSH tunnel from your local laptop into the GCE instance connecting to
GKE:

```
ssh $HOST -L 8080:localhost:8080
```

To show the naive version, navigate to [localhost:8080](localhost:8080) from a browser.

To show the ML version, navigate to
[localhost:8080/kubeflow](localhost:8080/kubeflow) from a browser.


