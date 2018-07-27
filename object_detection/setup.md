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
We have prepared a set of ksonnet prototypes to create a persistent volume and copy the data to it.
The prototypes can be found at the [obj-detection](./obj-detection) directory.
We will start creating a set of components and we will apply them in order for better results.

Create a PVC to store the data. This step assumes that you K8s cluster has [Dynamic Volume Provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/) enabled.
```
# First create the PVC component and apply it to create a PVC where the training data will be stored
ks generate pvc pets-pvc --storage="20Gi" --accessMode="ReadWriteMany"
ks apply ${ENV} -c pets-pvc
```
The commands above will create a PVC with `ReadWriteMany` access mode if your Kubernetes cluster
does not support this feature you can modify the `--accessMode` value to create the PVC in `ReadWriteOnce`
and before you execute the tf-job to train the model add a `nodeSelector:` configuration to execute the pods
in the same node. You can find more about assigning pods to specific nodes [here](https://kubernetes.io/docs/concepts/configuration/assign-pod-node/)

Now we will get the data we need to prepare our training pipeline:

```
# Create the component a get-data component and apply it, this component will download
# the dataset, annotations, the model we will use for the fine tune checkpoint, and
# the pipeline configration file

ks generate get-data-job get-data-job \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--urlData="http://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz" \
--urlAnnotations="http://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz" \
--urlModel="http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_coco_2018_01_28.tar.gz" \
--urlPipelineConfig="https://raw.githubusercontent.com/kubeflow/examples/master/object_detection/conf/faster_rcnn_resnet101_pets.config"

ks apply ${ENV} -c get-data-job

```
The command avobe will launch a set of Kubernetes batch jobs. Before moving to the next set of commands
make sure all of the jobs to get the data were completed.

The next command will generate a component to decompress the data that was downloaded after applying the
`get-data-job` component.


```
# Generate and apply the decompression jobs

ks generate decompress-data-job decompress-data-job \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--pathToDataset="/pets_data/images.tar.gz" \
--pathToAnnotations="/pets_data/annotations.tar.gz" \
--pathToModel="/pets_data/faster_rcnn_resnet101_coco_2018_01_28.tar.gz"

# Apply the components
ks apply ${ENV} -c decompress-data-job
```

Finally, we just need to create the pet records:

```
# Generate the component to create the pet record for the training pipeline

ks generate generic-job  create-pet-record-job \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--image="lcastell/pets_object_detection" \
--command='["python", "/models/research/object_detection/dataset_tools/create_pet_tf_record.py"]' \
--args='["--label_map_path=models/research/object_detection/data/pet_label_map.pbtxt", \
"--data_dir=/pets_data", \
"--output_dir=/pets_data"]'

ks apply ${ENV} -c create-pet-record-job

```

## Next
[Submit the TF Job](submit_job.md)
