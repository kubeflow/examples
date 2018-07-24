# Launch a distributed object detection training job
## Requirements

 - Docker 
 - Docker Registry
 - Object Detection Training Docker Image

Build the TensorFlow object detection training image, or use the pre-built image `lcastell/pets_object_detection` in Docker hub.

## To build the image:
First copy the Dockerfile file from `./docker` directory into your $HOME path
```
# from your $HOME directory
docker build --pull -t $USER/pets_object_detection -f ./Dockerfile .
```

### Push the image to your docker registry
```
# from your $HOME directory
docker tag  $USER/pets_object_detection  <your_server:your_port>/pets_object_detection
docker push <your_server:your_port>/pets_object_detection
```

## Create  training TF-Job deployment and launching it
**NOTE:** You can skip this step and copy the [pets-training.yaml](./jobs/pets-training.yaml) from the `jobs` directory and modify it to your needs.
Or simply run:

```
kubectl -n kubeflow apply -f ./jobs/pets-training.yaml
```

### Follow these steps to generate the tf-job manifest file:

Generate the ksonnet component using the tf-job prototype
```
# from the my-kubeflow directory
ks generate tf-training-job pets-training \
--image=<your_server:your_port>/pets_object_detection \
--numWorkers=1 \
--numPs=1 \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--pipelineConfigPath="/pets_data/faster_rcnn_resnet101_pets.config" \
--trainDir="/pets_data/train"
```
To see the yaml manifest you can dump the generated component into a K8s deployment manifest file.
```
ks show ${ENV} -c pets-training > pets-training.yaml
cat ./pets-training.yaml
```
At the end you should have something similar to [this](./jobs/pets-training.yaml)

No you can submit the TF-Job to K8s:
```
ks apply ${ENV} -c pets-training
# OR
kubectl -n kubeflow apply -f pets-training.yaml
```

For GPU support change use the `--numGpu=<number of Gpus to request>` param like:
```
# from the my-kubeflow directory
ks generate tf-training-job pets-training --name=pets-traning \
--namespace=kubeflow \
--image=<your_server:your_port>/pets_object_detection_gpu \
--numWorkers= 1 \
--numPs= 1 \
--numGpu=1 \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--pipelineConfigPath="/pets_data/faster_rcnn_resnet101_pets.config" \
--trainDir="/pets_data/train"
```

## Next
[Monitor your job](monitor_job.md)