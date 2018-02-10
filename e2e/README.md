# Tensorflow Workflow

# Storing artifacts in S3

Before you can use S3 for storing artifacts with argo, you must create a secret with AWS credentials for your bucket.
```
kubectl create secret generic aws-creds -n argo --from-literal=accessKey=${AWS_ACCESS_KEY_ID} --from-literal=secretKey=${AWS_SECRET_ACCESS_KEY}
```

Next you should install argo with the argo config in this repo.
```shell
kubectl create -f argo-config.yaml
argo install --install-namespace argo
```
