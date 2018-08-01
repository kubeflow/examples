# Launch a object detection batch prediction job using GPU.

## Setup

Requirements:

 - K8s cluster with GPUs.
 - Docker
 - Docker Registry
 - Kubeflow Batch prediction Docker Image
 - A model in SavedModel format

 This example shows how to run batch prediction to do object detection on a
 pre-trained model in a K8s cluster using GPU. See the [guide](https://www.kubeflow.org/docs/started/getting-started-gke/) to customize Kubeflow deployment to add GPU nodes.

 As Kubeflow batch-predict is [apache-beam](https://beam.apache.org/)-based, we
 are using local runner to run the job in the K8s cluser in this example. One can, however,
 choose different
 [runners](https://beam.apache.org/documentation/runners/capability-matrix/) to run the job remotely, such as [Google Dataflow](https://cloud.google.com/dataflow/). As of July 2018, Google Dataflow does not support GPUs.

### Build and push the image
Build a kubeflow batch prediction image, or use the [pre-built
image](https://gcr.io/kubeflow-examples/batch-predict) at Google Container
Registry (GCR). Following is an example to use GCR to host the image.

```
IMAGE="gcr.io/${YOUR_GCP_PROJECT}/batch-predict"
docker build -t ${IMAGE} -f ./Dockerfile.batch-predict .
docker push ${IMAGE}
```

### Prepare the model
The model used in this example can be downloaded from
[here](gs://kubeflow-examples-data/object-detection-coco/image_string_model). It is a slightly
modified version from [faster RCNN object detection model](http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_coco_2018_01_28.tar.gz) from [TensorFlow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md). This model accepts jpeg bytes as its input data.

Alternatively, you can follow the steps to [export a model](./export_tf_graph.md) from
checkpoint files from your [training jobs](./submit_job.md), or download a pre-trained model in
SavedModel format from Object Detection model zoo. The latter accepts numpy arrays of images bits, instead of jpeg bytes.

Refer this [blog](https://cloud.google.com/blog/big-data/2017/09/performing-prediction-with-tensorflow-object-detection-models-on-google-cloud-machine-learning-engine) for exporting a model in SavedModel format, in particular, how to change the input format from the default.

### Prepare the input data
In this example, the input tensor is jpeg image strings. So we pack the image bytes into TF-records. The input files contains 150 images and can be downloaded from [here](gs://kubeflow-examples-data/object-detection-coco/data/object-detection-images.tfrecord).

Refer this [blog](https://cloud.google.com/blog/big-data/2017/09/performing-prediction-with-tensorflow-object-detection-models-on-google-cloud-machine-learning-engine) for converting images into the input data the model can consume.

## Launch batch prediction job.
Customize [batch-predict.yaml](./batch-predict/batch-predict.yaml) to add the
paths to the model, the input image files, the input format, and the output
locations. Simply run:

```
kubectl -n <your_name_space> apply -f ./batch-predict/batch-predict.yaml
```

## Arguments

### --input_file_patterns

The list of input files or file patterns, separated by commas.

### --input_file_format
One of the following formats: json, tfrecord, and tfrecord_gzip. For the model in this example, the input is a jpeg-encoded image string tensor. The input file contains TF records of JPEG bytes. If you use the model from the [Object Detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) directly, the input is an numpy array instead. Then, your input file should contain multiple arrays. So the input format should be json. [Here](gs://kubeflow-examples-data/object-detection-coco/data/object-detection-images.json) is a sample input, which contains two images.

### --model_dir
The directory contains the model files in SavedModel format.

### --batch_size
Number of records in one batch in the input data. Depending on the memory in
your machine, it is recommend to be 1 to 4, up to 8.

### --output_result_prefix
Output path to save the prediction results.

### --output_error_prefix
Output path to save the prediction errors.

For more flags available to Kubeflow batch predict, please refer the [user
guide](https://www.kubeflow.org/docs/about/user_guide)

##  Monitoring jobs and visualize the detection results.
Once you submit the job, you can check the status and log of the pod that runs the
batch-predict job:

```
kubectl log <your-pod-name>
```

When the pod status is "complete", then check the result and error files to see
if the job is successful.

You can use [this script](./serving_script/visualization_utils.py) to visualize the detection boxes from the prediction results files on images.

