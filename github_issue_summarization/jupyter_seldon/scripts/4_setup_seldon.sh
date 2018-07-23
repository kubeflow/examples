#!/bin/bash

# Add Seldon Core to an existing kubeflow cluster

NAMESPACE=${KF_DEV_NAMESPACE}
KF_ENV=cloud

cd ks-kubeflow

# Gives cluster-admin role to the default service account in the ${NAMESPACE}
kubectl create clusterrolebinding seldon-admin --clusterrole=cluster-admin --serviceaccount=${NAMESPACE}:default
# Install the kubeflow/seldon package
ks pkg install kubeflow/seldon
# Generate the seldon component and deploy it
ks generate seldon seldon --name=seldon --namespace=${NAMESPACE}
ks apply ${KF_ENV} -c seldon

