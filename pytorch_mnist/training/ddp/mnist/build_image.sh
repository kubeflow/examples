#!/bin/bash
#
# A simple script to build the Docker images.
# This is intended to be invoked as a step in Argo to build the docker image.
#
# build_image.sh ${DOCKERFILE} ${IMAGE} ${TAG}
set -ex

DOCKERFILE=$1
IMAGE=$2
TAG=$3
CONTEXT_DIR=$(dirname "$DOCKERFILE")
PROJECT="${GCP_PROJECT}"

gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

cd $CONTEXT_DIR

echo "GCP Project: "$PROJECT

# Build CPU image
echo "Building CPU image using gcloud build"
gcloud builds submit --timeout=2h --machine-type=n1-highcpu-32 --tag=${IMAGE}:${TAG} --project=${PROJECT} cpu
echo "Finished building CPU image"

# Build GPU image
echo "Building GPU image using gcloud build"
gcloud builds submit --timeout=2h --machine-type=n1-highcpu-32 --tag=${IMAGE}:${TAG} --project=${PROJECT} gpu
echo "Finished building GPU image"