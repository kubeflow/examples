#!/bin/bash

# Setup a shared persistent disk

PROJECT=${KF_DEV_PROJECT}
ZONE=${KF_DEV_ZONE}
NAMESPACE=${KF_DEV_NAMESPACE}
KF_ENV=cloud
PD_DISK_NAME=github-issues-data-${NAMESPACE}

# Create the disk
gcloud --project=${PROJECT} compute disks create  --zone=${ZONE} ${PD_DISK_NAME} --description="PD for storing GitHub Issue data." --size=10GB

# Configure the environment to use the disk
cd ks-kubeflow
ks param set --env=${KF_ENV} kubeflow-core disks ${PD_DISK_NAME}
ks apply ${KF_ENV}

# Recreate the tf-hub pod so that it picks up the disk config
kubectl delete pod tf-hub-0 --namespace=${NAMESPACE}

