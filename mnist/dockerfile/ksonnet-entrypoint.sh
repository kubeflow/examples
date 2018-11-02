#!/bin/bash

#FIXME this is set to tf-user by default in order to work around lack of Serviceaccount setting in argo.
SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-tf-user}

kubectl config set-cluster $SERVICE_ACCOUNT --server=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT_HTTPS --insecure-skip-tls-verify=true
kubectl config set-context $SERVICE_ACCOUNT --cluster=$SERVICE_ACCOUNT
kubectl config set-credentials $SERVICE_ACCOUNT --token=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
kubectl config set-context $SERVICE_ACCOUNT --user=$SERVICE_ACCOUNT
kubectl config use-context $SERVICE_ACCOUNT

exec /bin/bash "$@"
