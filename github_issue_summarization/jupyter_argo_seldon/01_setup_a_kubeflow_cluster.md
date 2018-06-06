# Setup Kubeflow

In this part, you will setup kubeflow on an existing kubernetes cluster.

## Requirements

*   A kubernetes cluster
*   `kubectl` CLI (command line interface) pointing to the kubernetes cluster
    *   Make sure that you can run `kubectl get nodes` from your terminal
        successfully
*   The ksonnet CLI, v0.9.2 or higher: [ks](https://ksonnet.io/#get-started)

## Kubeflow setup

Refer to the [user
guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) for
detailed instructions on how to setup kubeflow on your kubernetes cluster.
Specifically, complete the following sections:

*    [Deploy
Kubeflow](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#deploy-kubeflow)
    *   The `ks-kubeflow` directory can be used instead of creating a ksonnet
        app from scratch.
    *   If you run into
        [API rate limiting errors](https://github.com/ksonnet/ksonnet/blob/master/docs/troubleshooting.md#github-rate-limiting-errors),
        ensure you have a `${GITHUB_TOKEN}` environment variable set.
    *   If you run into
        [RBAC permissions issues](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#rbac-clusters)
        running `ks apply` commands, be sure you have created a `cluster-admin` ClusterRoleBinding for your username.
*    [Setup a persistent disk](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#advanced-customization)
    *   We need a shared persistent disk to store our training data since
        containers' filesystems are ephemeral and don't have a lot of storage space.
    *   For this example, provision a `10GB` cluster-wide shared NFS mount with the
        name `github-issues-data`.
    *   After the NFS is ready, delete the `tf-hub-0` pod so that it gets recreated and
        picks up the NFS mount. You can delete it by running `kubectl delete pod
        tf-hub-0 -n=${NAMESPACE}`
*    [Bringing up a
Notebook](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#bringing-up-a-jupyter-notebook)
    *   When choosing an image for your cluster in the JupyterHub UI, use the
        image from this example:
        [`gcr.io/kubeflow-dev/issue-summarization-notebook-cpu:latest`](https://github.com/kubeflow/examples/blob/master/github_issue_summarization/workflow/Dockerfile).

After completing that, you should have the following ready:

*   A ksonnet app in a directory named `ks-kubeflow`
*   An output similar to this for `kubectl get pods` command

```commandline
NAME                                   READY     STATUS              RESTARTS   AGE
ambassador-75bb54594-dnxsd             2/2       Running             0          3m
ambassador-75bb54594-hjj6m             2/2       Running             0          3m
ambassador-75bb54594-z948h             2/2       Running             0          3m
jupyter-chasm                          1/1       Running             0          49s
spartakus-volunteer-565b99cd69-knjf2   1/1       Running             0          3m
tf-hub-0                               1/1       Running             0          3m
tf-job-dashboard-6c757d8684-d299l      1/1       Running             0          3m
tf-job-operator-77776c8446-lpprm       1/1       Running             0          3m
```

*   A Jupyter Notebook accessible at http://127.0.0.1:8000
*   A 10GB mount `/mnt/github-issues-data` in your Jupyter Notebook pod. Check this
    by running `!df` in your Jupyter Notebook.

## Summary

*   We created a ksonnet app for our kubeflow deployment
*   We deployed the kubeflow-core component to our kubernetes cluster
*   We created a disk for storing our training data
*   We connected to JupyterHub and spawned a new Jupyter notebook

*Next*: [Training the model](02_training_the_model.md)
