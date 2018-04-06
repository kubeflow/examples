#!/bin/bash

SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-default}

create-kubeconfig ${SERVICE_ACCOUNT} > kubeconfig.tmp
cp kubeconfig.tmp ~/.kube/config

kubectl config set-cluster default --server="https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}"

exec /bin/bash "$@"
