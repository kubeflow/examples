# Launch a distributed object detection training job
## Requirements

 - Docker 
 - Docker Registry
 - Object Detection Training Docker Image

### Build the TensorFlow object detection training image or use the pre-built image at `lcastell/pets_object_detection`.
### To build the image:
First copy the Dockerfile file from `./docker` directory into your $HOME path
```
# from your $HOME directory
docker build --pull -t $USER/object-detection-training -f ./Dockerfile .
```

### Push the image to your docker registry
```
# from your HOME directory
docker tag  $USER/object-detection-training  <your_server:your_port>/object-detection-training
docker push <your_server:your_port>/object-detection-training
```

## Create  training TF-Job deployment and launching it
**NOTE:** you can skip this step and copy the [pets-training.yaml](./conf/pets-training.yaml) from the `conf` directory and modify it to your needs.
Or simply run:

```
kubectl -n kubeflow apply -f ./conf/pets-training.yaml
```

### Follow these steps to generate the tf-job manifest file:

Generate the ksonnet component using the tf-job prototype
```
# from the my-kubeflow directory
ks generate tf-job pets-training --name=pets-traning \
--namespace=kubeflow \
--image=<your_server:your_port>/object-detection-training \
--num_masters=1 \
--num_workers= 1 \
--num_ps= 1
```
Dump the generated component into a K8s deployment manifest file.
```
ks show nocloud -c pets-training > pets-training.yaml
``` 
Add the volume mount information to the manifest file. We will be mounting `/pets_data` path to all the containers so they can pull the data for the training job
```
vim pets-training.yaml
```
Add the volume mounts information at the end you will be having a file like this: 
[pets-training.yaml](./conf/pets-training.yaml)

Submit the TF-Job to K8s:
```
kubectl -n kubeflow apply -f pets-training.yaml
```

## Next
[Monitor your job](monitor_job.md)