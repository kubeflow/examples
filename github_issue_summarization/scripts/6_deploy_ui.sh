#!/bin/bash

# Build and deploy a UI for accessing the trained model

PROJECT=${KF_DEV_PROJECT}
NAMESPACE=${KF_DEV_NAMESPACE}
KF_ENV=cloud

# Create the image locally
cd docker
docker build -t gcr.io/${PROJECT}/issue-summarization-ui-${NAMESPACE}:0.1 .

# Store in the container repo
gcloud docker -- push gcr.io/${PROJECT}/issue-summarization-ui-${NAMESPACE}:0.1

cd ../ks-kubeflow
ks param set ui github_token ${GITHUB_TOKEN} --env ${KF_ENV}
ks apply ${KF_ENV} -c ui

# Open access outside the cluster
kubectl port-forward $(kubectl get pods -n ${NAMESPACE} -l service=ambassador -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} 8080:80

