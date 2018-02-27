# Setup Kubeflow

In this part, you will setup kubeflow on an existing kubernetes cluster.

## Requirements

*   A kubernetes cluster
*   `kubectl` CLI pointing to the kubernetes cluster
    *   Make sure that you can run `kubectl get nodes` from your terminal
        successfully
*   The ksonnet CLI: [ks](https://ksonnet.io/#get-started)
*   `gcloud` CLI if using GCP

## Create a kubernetes namespace

We will do all our work in a new kubernetes namespace so that it doesn't overlap
with any existing kubernetes resources.

```
KUBE_NS=issue-summarization-model
kubectl create namespace ${KUBE_NS}
```

## Deploy Kubeflow

We will be using ksonnet(ks) to deploy kubeflow into your cluster.

Initialize a directory to contain your ksonnet application. This directory will
contain all the kubernetes manifests used to deploy kubeflow.

```
APP_NAME=kubeflow-app
ks init ${APP_NAME}
```

Install the kubeflow packages into your application.

```
cd ${APP_NAME}
# Add the kubeflow registry to the ksonnet app
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow
# Download the kubeflow/core ksonnet package
ks pkg install kubeflow/core
```

Create the kubeflow core component. We will do all our work in the
`issue-summarization-model` kubernetes namespace.

```
ks generate core kubeflow-core --name=kubeflow-core --namespace=${KUBE_NS}
```

ksonnet allows multiple
[environments](https://ksonnet.io/docs/concepts#environment), but for simplicity
we will be using the `default` environment for this tutorial.

```
KSONNET_ENV=default
ks env set ${KSONNET_ENV} --namespace ${KUBE_NS}
```

If using GKE, we can configure our cloud environment to use GCP features with a
single parameter:

```
ks param set kubeflow-core cloud gke --env=${KSONNET_ENV}
```

### Provision storage for training data

We need a shared persistent disk to store our training data since containers'
filesystems are ephemeral and don't have a lot of storage space.

If using Google Cloud, you can provision a persistent disk using the command

```
PD_DISK_NAME=github-issues-data
ZONE=<GCP zone in which kubernetes cluster is running>
PRODJECT=<GCP project in which kubernetes cluster is running>
gcloud --project=${PROJECT} compute disks create  --zone=${ZONE} ${PD_DISK_NAME} --description="PD to back NFS storage on GKE for GitHub Issues Data" --size=20GB
```

Configure the environment to use the disks.

```
ks param set --env=${KSONNET_ENV} kubeflow-core disks ${PD_DISK_NAME}
```

Let's deploy our kubeflow-core component to our cluster.

```
ks apply ${KSONNET_ENV} -c kubeflow-core
```

By deploying the kubeflow-core component, we are bringing up:

*   JupyterHub - This manages Jupyter Notebooks. This is not a Jupyter Notebook.
    Note the `Hub`.
*   TensorFlow job controller - This manages TensorFlow training jobs

If everything goes well you should see something like this:

```
kubectl get svc -n=${KUBE_NS}

NAME                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                              AGE
ambassador                        ClusterIP   10.35.244.92    <none>        80/TCP                               7m
ambassador-admin                  ClusterIP   10.35.254.230   <none>        8877/TCP                             7m
github-issues-data-disk-service   ClusterIP   10.35.244.21    <none>        2049/TCP,20048/TCP,111/TCP,111/UDP   7m
k8s-dashboard                     ClusterIP   10.35.250.6     <none>        443/TCP                              7m
tf-hub-0                          ClusterIP   None            <none>        8000/TCP                             7m
tf-hub-lb                         ClusterIP   10.35.248.177   <none>        80/TCP                               7m
```

## Connect to JupyterHub and spawn a Jupyter Notebook

Now that we have our services up and running, let's connect to JupyterHub to
spawn a Jupyter Notebook.

```
PODNAME=`kubectl get pods --namespace=${KUBE_NS} --selector="app=tf-hub" --output=template --template="{{with index .items 0}}{{.metadata.name}}{{end}}"`
kubectl port-forward --namespace=${KUBE_NS} $PODNAME 8000:8000
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

You should see a sign in prompt.

1.  Sign in using any username/password
1.  Click the "Start My Server" button, you will be greeted by a dialog screen.
1.  Set the image to `gcr.io/kubeflow/tensorflow-notebook-cpu:v1` or
    `gcr.io/kubeflow/tensorflow-notebook-gpu:8fbc341245695e482848ac3c2034a99f7c1e5763`
    depending on whether doing CPU or GPU training, or whether or not you have
    GPUs in your cluster.
1.  Allocate memory, CPU, GPU, or other resources according to your need (1 CPU
    and 2Gi of Memory are good starting points)
    *   To allocate GPUs, make sure that you have GPUs available in your cluster
    *   Run the following command to check if there are any nvidia gpus
        available: `kubectl get nodes
        "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"`
    *   If you have GPUs available, you can schedule your server on a GPU node
        by specifying the following json in `Extra Resource Limits` section:
        `{"nvidia.com/gpu": "1"}`
    *   Click Spawn
1.  Eventually you should now be greeted with a Jupyter interface. Note that the
    GPU image is several gigabytes in size and may take a few minutes to
    download and start.

## Summary

*   We created a ksonnet app for our kubeflow deployment
*   We created a disk for storing our training data
*   We deployed the kubeflow-core component to our kubernetes cluster
*   We connected to JupyterHub and spawned a new Jupyter notebook

## Troubleshooting

If you are running on a K8s cluster with [RBAC
enabled](https://kubernetes.io/docs/admin/authorization/rbac/#command-line-utilities),
you may get an error like the following when deploying Kubeflow:

```
ERROR Error updating roles kubeflow-test-infra.jupyter-role: roles.rbac.authorization.k8s.io "jupyter-role" is forbidden: attempt to grant extra privileges: [PolicyRule{Resources:["*"], APIGroups:["*"], Verbs:["*"]}] user=&{your-user@acme.com  [system:authenticated] map[]} ownerrules=[PolicyRule{Resources:["selfsubjectaccessreviews"], APIGroups:["authorization.k8s.io"], Verbs:["create"]} PolicyRule{NonResourceURLs:["/api" "/api/*" "/apis" "/apis/*" "/healthz" "/swagger-2.0.0.pb-v1" "/swagger.json" "/swaggerapi" "/swaggerapi/*" "/version"], Verbs:["get"]}] ruleResolutionErrors=[]
```

This error indicates you do not have sufficient permissions. In many cases you
can resolve this just by creating an appropriate clusterrole binding like so and
then redeploying kubeflow

```
kubectl create clusterrolebinding default-admin --clusterrole=cluster-admin --user=your-user@acme.com
```

Replace `your-user@acme.com` with the user listed in the error message.
