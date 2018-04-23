#!/bin/bash

# Instantiates a fresh version of kubeflow on a cluster

KF_VERSION=v0.1.0
NAMESPACE=${KF_DEV_NAMESPACE}
KF_ENV=cloud

# Initialize an empty ksonnet app
ks version
ks init ks-kubeflow

# Install kubeflow core package
cd ks-kubeflow
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${KF_VERSION}/kubeflow
ks pkg install kubeflow/core@${KF_VERSION}

# Generate core component
ks generate core kubeflow-core --name=kubeflow-core

# Enable anonymous usage metrics
ks param set kubeflow-core reportUsage true
ks param set kubeflow-core usageId $(uuidgen)

# Define an environment
ks env add ${KF_ENV}

# Configure our cloud to use GCP features
ks param set kubeflow-core cloud gke --env=${KF_ENV}

# Set Jupyter storageclass
ks param set kubeflow-core jupyterNotebookPVCMount /home/jovyan/work

# Create a namespace for my deployment
kubectl create namespace ${NAMESPACE}
ks env set ${KF_ENV} --namespace ${NAMESPACE}

# Instantiate objects on the cluster
ks apply ${KF_ENV} -c kubeflow-core


