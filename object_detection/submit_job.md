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

### Follow these steps to generate the tf-training-job component:

Generate the ksonnet component using the tf-training-job [prototype](obj-detection/prototypes/tf-tranining-job.jsonnet)
```
# from the my-kubeflow directory
ks generate tf-training-job pets-training \
--image=<your_server:your_port>/pets_object_detection \
--numWorkers=1 \
--numPs=1 \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--pipelineConfigPath="/pets_data/faster_rcnn_resnet101_pets.config" \
--trainDir="/pets_data/train"
```
To see the yaml manifest you can dump the generated component into a K8s deployment manifest file.
```
ks show ${ENV} -c pets-training > pets-training.yaml
cat ./pets-training.yaml
```
No you can submit the TF-Job to K8s:
```
ks apply ${ENV} -c pets-training
# OR
kubectl apply -f pets-training.yaml
```

For GPU support use the `--numGpu=<number of Gpus to request>` param like:
```
# from the my-kubeflow directory
ks generate tf-training-job pets-training \
--image=<your_server:your_port>/pets_object_detection_gpu \
--numWorkers=1 \
--numPs=1 \
--numGpu=1 \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--pipelineConfigPath="/pets_data/faster_rcnn_resnet101_pets.config" \
--trainDir="/pets_data/train"
```

## Next
[Monitor your job](monitor_job.md)