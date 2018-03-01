# Teardown

Delete the kubernetes namespace

```
kubectl delete namespace ${NAMESPACE}
```

Delete the PD backing the NFS mount

```
gcloud --project=${PROJECT} compute disks delete  --zone=${ZONE} ${PD_DISK_NAME}

```

Delete the kubeflow-app directory

```
rm -rf my-kubeflow
```
