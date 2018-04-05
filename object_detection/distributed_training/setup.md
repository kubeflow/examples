## Setup Kubeflow
### Requirements

 - Kubernetes cluster
 - Access to a working `kubectl` (Kubernetes CLI)
 - Ksonnet CLI: [ks](https://ksonnet.io/)

### Setup
Refer to the [user guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md) for instructions on how to setup kubeflow on your kubernetes cluster. Specifically, look at section [deploy kubeflow](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md#deploy-kubeflow). 
For this example we will be using ks `nocloud` environment. If you plan to use `cloud` ks environment, please make sure you follow the proper instructions in the kubeflow user guide.

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
Pull a sample dataset and store it on all cluster nodes in the same path 
In this case, we will be storing the data in `/tmp/pets` directory. 
```
git clone https://github.com/tensorflow/models.git
wget http://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz
wget http://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz
mkdir -p /tmp/pets
tar -xvf images.tar.gz -C /tmp/pets
tar -xvf annotations.tar.gz -C /tmp/pets

python models/research/object_detection/dataset_tools/create_pet_tf_record.py --label_map_path=models/research/object_detection/data/pet_label_map.pbtxt --data_dir=/tmp/pets  --output_dir=/tmp/pets
``` 

Copy the `./conf/faster_rcnn_resnet101_pets.config` from the `conf` directory into your $HOME path.

Modify the pipeline training file and copy it to `/tmp/pets`
```
wget http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_coco_2018_01_28.tar.gz
tar -xf faster_rcnn_resnet101_coco_2018_01_28.tar.gz -C /tmp/pets
cp models/research/object_detection/data/pet_label_map.pbtxt /tmp/pets/
cp $HOME/faster_rcnn_resnet101_pets.config /tmp/pets/
```
After completing these steps for one of your cluster nodes, copy the directory to all the remaining nodes.

## Next
[Submit the TF Job](submit_job.md)