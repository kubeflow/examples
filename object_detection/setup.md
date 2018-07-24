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
### Adding objectDetection package to your Ksonnet app

```
# Add the registry
ks registry add objectDetection github.com/kuebflow/examples/tree/master/object_detection

#install the package
ks pkg install objectDetection/obj-detection
```

## Preparing the training data
We have prepared a set of ksonnet prototypes to create a persistent volume and copy the data to it.
The prototypes can be found at [obj-detection](./obj-detection) directory. We will create a set of components and we will apply them in order for better results.

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
# Create the components and apply them
ks generate get-data-job get-dataset-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--url="http://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz"

ks generate get-data-job get-annotations-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--url="http://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz"

ks generate get-data-job get-model-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--url="http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_coco_2018_01_28.tar.gz"

ks apply ${ENV} -c get-dataset-job
ks apply ${ENV} -c get-annotations-job
ks apply ${ENV} -c get-model-job

```

```
# Generate and apply the decompression jobs

ks generate decompress-data-job decompress-dataset-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--pathToFile="/pets-data/images.tar.gz"

ks generate decompress-data-job decompress-annotations-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--pathToFile="/pets-data/annotations.tar.gz"

ks generate decompress-data-job decompress-model-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--pathToFile="/pets-data/faster_rcnn_resnet101_coco_2018_01_28.tar.gz"

# Apply the components
ks apply ${ENV} -c decompress-dataset-job
ks apply ${ENV} -c decompress-annotations-job
ks apply ${ENV} -c decompress-model-job
```

```
# Create the components to configure the training pipeline
ks generate get-data-job get-pipeline-config-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--url="https://raw.githubusercontent.com/kubeflow/examples/master/object_detection/conf/faster_rcnn_resnet101_pets.config"

# Create pet record
ks generate generic-job  create-pet-record-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--image="lcastell/pets_object_detection" \
--command='["python", "/models/research/object_detection/dataset_tools/create_pet_tf_record.py"]' \
--args='["--label_map_path=models/research/object_detection/data/pet_label_map.pbtxt", \
"--data_dir=/pets_data", \
"--output_dir=/pets_data"]'

ks apply ${ENV} -c get-pipeline-config-job
ks apply ${ENV} -c create-pet-record-job

```

## Next
[Submit the TF Job](submit_job.md)
