#!/usr/bin/env bash

TAG=$1
GCLOUD_PROJECT=${GCLOUD_PROJECT:-kubeflow-public-images}

echo 'Deploying kubeflow...'
kf delete
kf generate
kf add pkg tensorboard
kf add pkg jobs
kf add module mnist using jobs/[single-job --jobName=mnist --jobImage=gcr.io/${GCLOUD_PROJECT}/kubeflow-train:${TAG}]
echo 'Deploying mnist module ...'
kf apply
