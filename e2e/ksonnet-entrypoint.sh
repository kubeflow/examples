#!/bin/bash

SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-argo}

create-kubeconfig ${SERVICE_ACCOUNT} > kubeconfig.tmp
cp kubeconfig.tmp ~/.kube/config

kubectl config set-cluster default --server="https://kubernetes"

exec /bin/bash "$@"
