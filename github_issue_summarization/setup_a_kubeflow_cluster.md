# Setup Kubeflow

In this part, you will setup kubeflow on an existing kubernetes cluster.

## Requirements

*   A kubernetes cluster
*   `kubectl` CLI pointing to the kubernetes cluster
    *   Make sure that you can run `kubectl get nodes` from your terminal
        successfully
*   The ksonnet CLI: [ks](https://ksonnet.io/#get-started)

Refer to the [user
guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) for
instructions on how to setup Kubeflow on your Kubernetes Cluster. Specifically
complete the [Deploy
Kubeflow](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#deploy-kubeflow)
section and [Bringing up a
Notebook](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#bringing-up-a-notebook)
section.

After completing that, you should have the following ready

*   A ksonnet app in a directory named `my-kubeflow`
*   An output similar to this for `kubectl get pods`

```
NAME                              READY     STATUS    RESTARTS   AGE
ambassador-7987df44b9-4pht8       2/2       Running   0          1m
ambassador-7987df44b9-dh5h6       2/2       Running   0          1m
ambassador-7987df44b9-qrgsm       2/2       Running   0          1m
tf-hub-0                          1/1       Running   0          1m
tf-job-operator-78757955b-qkg7s   1/1       Running   0          1m
```

*   A Jupyter Notebook accessible at `http://127.0.0.1:8000`

## Provision storage for training data

We need a shared persistent disk to store our training data since containers'
filesystems are ephemeral and don't have a lot of storage space.

The [Advanced
Customization](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#advanced-customization)
section of the [user
guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) has
instructions on how to provision a cluster-wide shared NFS.

For this example, provision a `10GB` NFS mount with the name
`github-issues-data`.

After the NFS is ready, delete the `tf-hub-0` pod so that it gets recreated and
picks up the NFS mount. You can delete it by running `kubectl delete pod
tf-hub-0 -n=${NAMESPACE}`

At this point you should have a 10GB mount `/mnt/github-issues-data` in your
Jupyter Notebook pod. Check this by running `!df` in your Jupyter Notebook.

## Summary

*   We created a ksonnet app for our kubeflow deployment
*   We created a disk for storing our training data
*   We deployed the kubeflow-core component to our kubernetes cluster
*   We connected to JupyterHub and spawned a new Jupyter notebook

Next: [Training the model using our cluster](training_the_model.md)
