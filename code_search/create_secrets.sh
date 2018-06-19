#!/usr/bin/env bash

set -ex

export PROJECT=${PROJECT:-}
export SA_NAME=code-search-access
export SA_EMAIL=${SA_NAME}@${PROJECT}.iam.gserviceaccount.com
export SA_KEY_FILE=${SA_EMAIL}.key.json


if [[ "${1}" = "-d" ]]; then
  kubectl delete secret gcp-credentials gcp-registry-credentials

  rm ${SA_KEY_FILE}

  gcloud projects remove-iam-policy-binding ${PROJECT} \
    --member=serviceAccount:${SA_EMAIL} \
    --role=roles/storage.admin

  gcloud iam service-accounts delete ${SA_EMAIL} --quiet

  exit 0
fi


gcloud iam service-accounts create ${SA_NAME} --display-name ${SA_EMAIL}

gcloud projects add-iam-policy-binding ${PROJECT} \
  --member=serviceAccount:${SA_EMAIL} \
  --role=roles/storage.admin

gcloud iam service-accounts keys create ${SA_KEY_FILE} \
  --iam-account=${SA_EMAIL}

kubectl create secret docker-registry gcp-registry-credentials \
  --docker-server=https://gcr.io \
  --docker-username=_json_key \
  --docker-password="$(cat ${SA_KEY_FILE})" \
  --docker-email=${SA_EMAIL}

kubectl create secret generic gcp-credentials \
  --from-file=key.json="${SA_KEY_FILE}"

