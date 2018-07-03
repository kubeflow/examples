## Setup Kubeflow
### Requirements

 - Kubernetes cluster
 - Access to a working `kubectl` (Kubernetes CLI)
 - Ksonnet CLI: [ks](https://ksonnet.io/)

### Setup
Refer to the [user guide](https://www.kubeflow.org/docs/about/user_guide) for instructions on how to setup kubeflow on your kubernetes cluster. Specifically, look at the section on [deploying kubeflow](https://www.kubeflow.org/docs/about/user_guide#deploy-kubeflow).
For this example, we will be using ks `nocloud` environment. If you plan to use `cloud` ks environment, please make sure you follow the proper instructions in the kubeflow user guide.

After completing the steps in the kubeflow user guide you will have the following:
- A ksonnet app directory called `my-kubeflow` 
- A new namespace in you K8s cluster called `kubeflow`
- The following pods in your kubernetes cluster in the `kubeflow` namespace:
```
kubectl -n kubeflow get pods
NAME                              READY     STATUS    RESTARTS   AGE
ambassador-7987df44b9-4pht8       2/2       Running   0          1m
ambassador-7987df44b9-dh5h6       2/2       Running   0          1m
ambassador-7987df44b9-qrgsm       2/2       Running   0          1m
tf-hub-0                          1/1       Running   0          1m
tf-job-operator-78757955b-qkg7s   1/1       Running   0          1m
```
## Preparing the training data
We have prepared a set of K8s batch jobs to create a persistent volume and copy the data to it.
The `yaml` manifest files for these jobs can be found at [jobs](./jobs) directory. These `yaml` files are numbered and must be executed in order.

```
# First create the PVC where the training data will be stored
kubectl -n kubeflow apply -f ./jobs/00create-pvc.yaml
```
The 00create-pvc.yaml creates a PVC with `ReadWriteMany` access mode if your Kubernetes cluster
does not support this feature you can modify the manifest to create the PVC in `ReadWriteOnce`
and before you execute the tf-job to train the model add a `nodeSelector:` configuration to execute the pods
in the same node. You can find more about assigning pods to specific nodes [here](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/)

```
# Get the dataset, annotations and faster-rcnn-model tars
kubectl -n kubeflow apply -f ./jobs/01get-dataset.yaml
kubectl -n kubeflow apply -f ./jobs/02get-annotations.yaml
kubectl -n kubeflow apply -f ./jobs/03get-model-job.yaml
```

```
# Decompress tar files
kubectl -n kubeflow apply -f ./jobs/04decompress-images.yaml
kubectl -n kubeflow apply -f ./jobs/05decompress-annotations.yaml
kubectl -n kubeflow apply -f ./jobs/06decompress-model.yaml
```

```
# Configuring the training pipeline
kubectl -n kubeflow apply -f ./jobs/07get-fasterrcnn-config.yaml
kubectl -n kubeflow apply -f ./jobs/08create-pet-record.yaml
```

## Next
[Submit the TF Job](submit_job.md)
