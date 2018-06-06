# Teardown

Delete the kubernetes `namespace`.

```commandline
kubectl delete namespace ${NAMESPACE}
```

Delete the PD (persistent data) backing the NFS mount.

```commandline
gcloud --project=${PROJECT} compute disks delete  --zone=${ZONE} ${PD_DISK_NAME}
```

Delete the `kubeflow-app` directory.

```commandline
rm -rf my-kubeflow
```

*Back*: [Querying the model](04_querying_the_model.md)
