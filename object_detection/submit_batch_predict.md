# Launch a object detection batch prediction job
## Requirements

 - Docker
 - Docker Registry
 - Kubeflow Batch prediction Docker Image

Build a kubeflow batch prediction image, or use the pre-built images at
[gcr.io](https://pantheon.corp.google.com/gcr/images/cloud-ml-yxshi/GLOBAL/kubeflow-batch-predict?project=cloud-ml-yxshi)

## build the image:
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
One of the following formats: json, tfrecord, and tfrecord_gzip. For the model in this example, the input is a jpeg-encoded image string tensor. The input file contains TF records of JPEG bytes. If you use the model from the [Tensorflow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) directly, the input is an numpy array instead. Then, your input file should contain multiple arrays. So the input format should be json. [Here](https://) is a sample input, which contains two images.

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
