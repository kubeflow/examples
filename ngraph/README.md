# ngraph example

This example will create a docker image which, when deployed, will 
- train a mnist model using tensorflow with ngraph enabled.
- upload the trained model to a GCS bucket 
- bring up tensorboard to view the output

- MNIST.py
  - contains TensorFlow code to train a model and upload the results to a Google Cloud Storage bucket
- Dockerfile
  - Builds a container to run the MNIST job

---

Running `make run` will call run.sh which uses kubeflow to create a mnist module and deploy a single-job with this image

Ngraph declustered*.txt output can be viewed with the online model viewer [here](https://lutzroeder.github.io/netron/).
