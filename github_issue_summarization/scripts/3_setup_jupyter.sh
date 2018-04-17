#!/bin/bash

# Setup access to Jupyterhub from outside the cluster, primarily for viewing via
# a browser

NAMESPACE=${KF_DEV_NAMESPACE}

PODNAME=`kubectl get pods --namespace=${NAMESPACE} --selector="app=tf-hub" --output=template --template="{{with index .items 0}}{{.metadata.name}}{{end}}"`
kubectl port-forward --namespace=${NAMESPACE} $PODNAME 8000:8000


