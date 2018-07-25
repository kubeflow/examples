# Launch a object detection batch prediction job using GPU.

## Setup

Requirements:

 - K8s cluster with GPUs.
 - Docker
 - Docker Registry
 - Kubeflow Batch prediction Docker Image
 - A model in SavedModel format

 This example shows how to run a batch prediction job to do object detection on a
 pre-trained model in a k8s cluster. The inference time is about 1 second per image in a P100
 Nvidia GPU, 5 seconds on a K80 Nvdia GPU, as long as 5 mins on a CPU. So we
 strongly recommend you setup a K8s cluster with GPUs. Here is the [guide](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus) to setup a GKE cluster with GPUs.

### Build the image
Build a kubeflow batch prediction image, or use the pre-built images at
[gcr.io](https://pantheon.corp.google.com/gcr/images/cloud-ml-yxshi/GLOBAL/kubeflow-batch-predict?project=cloud-ml-yxshi)

First copy the Dockerfile.batch-predict file from `./docker` directory into your $HOME path
```
# from your $HOME directory
docker build --pull -t $USER/kubeflow-batch-predict -f ./Dockerfile.batch-predict .
```

### Push the image to your docker registry
```
# from your $HOME directory
docker tag  $USER/kubeflow-batch-predict <your_server:your_port>/kubeflow-batch-predict
docker push <your_server:your_port>/kubeflow-batch-predict
```

### Prepare the model
You can either follow the step to [export a model](./export_tf_graph.md) from
checkpoint files from your [training job](./submit_job.md), or download a pre-trained model in
SavedModel format from Object Detection [model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md). In this example, we downloaded checkpoint files from a [pre-trained model](http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_coco_2018_01_28.tar.gz) but changed the default [input type](https://github.com/tensorflow/models/blob/master/research/object_detection/export_inference_graph.py#L102) from "image_tensor" to "encoded_image_string_tensor" to reduce the input data size and exported to a new saved model.

Refer this [blog](https://cloud.google.com/blog/big-data/2017/09/performing-prediction-with-tensorflow-object-detection-models-on-google-cloud-machine-learning-engine) for exporting a model in SavedModel format.

### Prepare the input data
Depending on the input tensor(s) the model can consume, you can pack the images
accordingly. In this example, the input tensor is jpeg image strings. So we
pack the image bytes into TF-records.

Refer this [blog](https://cloud.google.com/blog/big-data/2017/09/performing-prediction-with-tensorflow-object-detection-models-on-google-cloud-machine-learning-engine) for converting images into the input data the model can consume.

## Launch batch prediction job.
Customize [batch-predict.yaml](./batch-predict/batch-predict.yaml) to add the
paths to your own model, the input image files, the input format, and the output
locations. Simply run:

```
kubectl -n <your_name_space> apply -f ./batch-predict/batch-predict.yaml
```

## Arguments

### --input_file_patterns

The list of input files. The wildcard may or may not work depending the file
system your input files reside.

### --input_file_format
One of the following formats: json, tfrecord, and tfrecord_gzip. For the model in this example, the input is a jpeg-encoded image string tensor. The input file contains TF records of JPEG bytes. If you use the model from the [Object Detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) directly, the input is an numpy array instead. Then, your input file should contain multiple arrays. So the input format should be json. [Here](https://) is a sample input, which contains two images.

### --model_dir
The directory contains the model files in SavedModel format.

### --batch_size
Number of records in one batch in the input data.

### --output_result_prefix
Output path to save the prediction results.

### --output_error_prefix
Output path to save the prediction errors.

For more flags available to Kubeflow batch predict, please refer the [user
guide](https://www.kubeflow.org/docs/about/user_guide)

##  Monitoring jobs
Once you submit the job, you can check the status and log of the pod that runs the
batch-predict job:

```
kubectl log <your-pod-name>
```

When the pod status is "complete", then check the result and error files to see
if the job is successful.

