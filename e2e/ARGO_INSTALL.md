# Tensorflow Workflow

# Storing artifacts in S3

Before you can use S3 compatible artifact repository for storing artifacts with argo, you must create a secret with your artifact repo credentials for your bucket.
```shell
ARTIFACT_REPO_ACCESS_KEY_ID='XXXXXXXXXX'
ARTIFACT_REPO_SECRET_ACCESS_KEY='XXXXXXXXXX'
kubectl create secret generic artifact-repo-creds  --from-literal=accessKey=${ARTIFACT_REPO_ACCESS_KEY_ID} --from-literal=secretKey=${ARTIFACT_REPO_SECRET_ACCESS_KEY}
```

Next you should install the argo config in this repo depending on your artifact repo.

For AWS stored artifact
```
kubectl create -f argo-config.yaml -n argo
```

For Google cloud Stored artifacts:
```
kubectl create -f argo-config-gcs.yaml -n argo
```

Then install Argo
```
argo install --install-namespace argo
```
