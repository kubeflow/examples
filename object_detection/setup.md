## Setup Kubeflow
### Requirements

 - Kubernetes cluster
 - Access to a working `kubectl` (Kubernetes CLI)
 - Ksonnet CLI: [ks](https://ksonnet.io/)

### Setup
Refer to the [user guide](https://www.kubeflow.org/docs/about/user_guide) for instructions on how to setup kubeflow on your kubernetes cluster. Specifically, look at the section on [deploying kubeflow](https://www.kubeflow.org/docs/about/user_guide#deploy-kubeflow).
For this example, we will be using ks `nocloud` environment (on premise K8s). If you plan to use `cloud` ks environment, please make sure you follow the proper instructions in the kubeflow user guide.

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
### Adding objectDetection package to your Ksonnet app

```
# Add the registry
ks registry add objectDetection github.com/kuebflow/examples/tree/master/object_detection

#install the package
ks pkg install objectDetection/obj-detection
```

## Preparing the training data
We have prepared a ksonnet app `ks-app` you can use to create a persistent volume and copy the data to it.
The prototypes can be found at the [obj-detection](./obj-detection) directory.

Create a PVC to store the data. This step assumes that you K8s cluster has [Dynamic Volume Provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/) enabled.
```
# First create the PVC component and apply it to create a PVC where the training data will be stored
ks apply ${ENV} -c pets-pvc
```

The available parameters for the above component are: `accessMode=ReadWriteMany` and `storage=20Gi`.
You can override these parameters with `ks set param` command.

By default the command above will create a PVC with `ReadWriteMany` access mode if your Kubernetes cluster
does not support this feature you can modify the `accessMode` value to create the PVC in `ReadWriteOnce`
and before you execute the tf-job to train the model add a `nodeSelector:` configuration to execute the pods
in the same node. You can find more about assigning pods to specific nodes [here](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/)

Now we will get the data we need to prepare our training pipeline:

```
# Apply the get-data-job component this component will download the dataset,
# annotations, the model we will use for the fine tune checkpoint, and
# the pipeline configuration file

ks apply ${ENV} -c get-data-job
```
The overridable parameters for the `get-data-job` component are:

- `mountPath` string, volume mount path.
- `pvc` string, name of the PVC where the data will be stored.
- `urlData` string, remote URL of the dataset that will be used for training.
- `urlAnnotations` string, remote URL of the annotations that will be used for training.
- `urlModel` string, remote URL of the model that will be used for fine tuning.
- `urlPipelineConfig` string, remote URL of the pipeline configuration file to use.

Before moving to the next set of commands make sure all of the jobs to get the data were completed.

Now we will apply the decompress data component:

```
# Apply the component
ks apply ${ENV} -c decompress-data-job
```

The overridable parameters for the `decompress-data-job` component are:

- `mountPath` string, volume mount path.
- `pvc` string, name of the PVC where the data is located.
- `pathToAnnotations` string, File system path to the annotations .tar.gz file
- `pathToDataset` string, File system path to the dataset .tar.gz file
- `pathToModel` string, File system path to the model .tar.gz file

Finally, we just need to create the pet records:

```
ks apply ${ENV} -c create-pet-record-job

```

```
ks generate generic-job  create-pet-record-job \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--image="lcastell/pets_object_detection" \
--command='["python", "/models/research/object_detection/dataset_tools/create_pet_tf_record.py"]' \
--args='["--label_map_path=models/research/object_detection/data/pet_label_map.pbtxt", \
"--data_dir=/pets_data", \
"--output_dir=/pets_data"]'
```

The overridable parameters for the `create-pet-record-job` component are:

- `mountPath` string, volume mount path.
- `pvc` string, name of the PVC where the data is located.
- `image` string, name of the docker image to use.
- `command` array, the command to use.
- `args` array, the command args to use.
- `data_dir` string, the directory with the images
- `output_dir` string, the output directory for the pet records.

To see the default values of the components used in this set of steps look at: [params.libsonnet](./ks-app/components/params.libsonnet)

## Next
[Submit the TF Job](submit_job.md)
