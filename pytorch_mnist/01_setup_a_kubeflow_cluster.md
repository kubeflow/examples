### Kubernetes Cluster Environment

Your cluster must:

- Be at least version 1.10
- Have access to an NFS mount (e.g. [Google Cloud Filestore](https://cloud.google.com/filestore/))
- Contain 3 nodes of at least 8 cores and 16 GB of RAM.
- GPU node pool to train the GPU example with at least 4 nodes (1 master + 3 workers)

If using GKE, the following will provision a cluster with the required features (Using v0.3.0 
release):

1. Follow v0.3.0 [instructions](https://v0-3.kubeflow.org/docs/started/getting-started-gke/)
2. To enable Seldon from the `ks_app` folder initialised in previous step
```
ks pkg install kubeflow/seldon
ks generate seldon seldon
ks apply default -c seldon
```

NOTE: You must be a Kubernetes admin to follow this guide. If you are not an admin, please contact your local cluster administrator for a client cert, or credentials to pass into the following commands:

```
$ kubectl config set-credentials <username> --username=<admin_username> --password=<admin_password>
$ kubectl config set-context <context_name> --cluster=<cluster_name> --user=<username> --namespace=<namespace>
$ kubectl config use-context <context_name>
```

### Local Setup

You also need the following command line tools:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [ksonnet](https://ksonnet.io/#get-started)

NOTE: These instructions rely on Github, and may cause issues if behind a firewall with many Github users. Make sure you [generate and export this token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/):

```
export GITHUB_TOKEN=xxxxxxxx
```
TODO