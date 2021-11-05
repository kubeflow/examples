#!/usr/bin/env bash

# run as root
apt-get update 
apt-get install -y wget

# use 3.2.x for install kubeflow
wget https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv3.2.3/kustomize_kustomize.v3.2.3_linux_amd64
chmod +x ./kustomize_kustomize.v3.2.3_linux_amd64 && \
  mv ./kustomize_kustomize.v3.2.3_linux_amd64 /usr/local/bin/kustomize

USER_NAME=$(who | awk {'print $1'})
KUBEFLOW_ROOT=/home/${USER_NAME}/kubeflow
KF_NAME=v1.3
KF_DIR=${KUBEFLOW_ROOT}/${KF_NAME}

mkdir -p $KF_DIR

cd $KF_DIR && \
  wget https://github.com/kubeflow/manifests/archive/refs/tags/v1.3.1.tar.gz && \
  tar -xzvf v1.3.1.tar.gz && \
  cd manifests-1.3.1  && \
  while ! kustomize build --load_restrictor=none example | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
