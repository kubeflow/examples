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

# Wait for the Docker daemon to be available.
until docker ps
do sleep 3
done

gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

cd $CONTEXT_DIR

echo "GCP Project: "$PROJECT

echo "Building image using gcloud build"
gcloud builds submit --timeout=2h --machine-type=n1-highcpu-32 --tag=${IMAGE}:${TAG} --project=${PROJECT} .
echo "Finished building image"