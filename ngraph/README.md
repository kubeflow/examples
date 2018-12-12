# ngraph example using gcp

This example will create a docker image which, when run, will 
- train a mnist model using tensorflow with ngraph enabled.
- save the model locally to /home/tensorflow/saved_model.pbtxt
- generate graph data under /home/tensorflow/output using saved_model.pbtxt
- bring up tensorboard to view the output

## prerequisites

- kfctl.sh needs to be in your path
- GCLOUD_PROJECT env variable needs to point to a gcr.io project that you can push the model to
- KUBEFLOW_DIR env variable needs to point to where kubeflow is installed

## files

- MNIST.py
  - contains TensorFlow code to train a model and upload the results to a Google Cloud Storage bucket
- MNIST.sh
  - container entry point, will run MNIST.py, convert output, run tensorboard
- Dockerfile
  - Builds a container to run the MNIST job and bring up tensorboard 
- run.sh
  - Created kubeflow namespace and deploys the kubeflow mnist component to this namespace

## expected output

- tensorboard should show a graph that looks like below:

Running `make run` will call run.sh which uses kubeflow to create a mnist module and deploy a single-job with this image

Ngraph declustered*.txt output can be viewed with the online model viewer [here](https://lutzroeder.github.io/netron/).
