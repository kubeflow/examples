# Distributed Training using tensor2tensor

[Tensor2Tensor](https://github.com/tensorflow/tensor2tensor), or
[T2T](https://github.com/tensorflow/tensor2tensor) for short, is a library
of deep learning models and datasets designed to make deep learning more
accessible and [accelerate ML
research](https://research.googleblog.com/2017/06/accelerating-deep-learning-research.html). To get started, follow the instructions on the tensor2tensor [README](https://github.com/tensorflow/tensor2tensor) and install it locally.

We are going to use the packaged [transformer](https://research.googleblog.com/2017/08/transformer-novel-neural-network.html) model to train our github issue summarization model.

## Defining a Problem
A key concept in the T2T library is that of a Problem, which ties together all the pieces needed to train a machine learning model. It is easiest to inherit from the appropriate base class in the T2T library and then change only the pieces that are different for your model. We are going to define a problem in [github_problem.py](tensor2tensor/github/github_problem.py) which will extend the inbuilt `text_problems.Text2TextProblem`. `github_problem.py` overrides some properties such as approx_vocab_size, generate_samples, etc.

## Generate training data

For training a model using tensor2tensor, the input data must be in a particular format. tensor2tensor comes with a data generator which transforms your input data into a format which can be consumed by the training process.

```
cd tensor2tensor/
mkdir csv_data
cd csv_data
wget https://storage.googleapis.com/kubeflow-examples/github-issue-summarization-data/github-issues.zip
unzip github-issues.zip
cd ..
DATA_DIR=data
TMP_DIR=tmp
mkdir -p $DATA_DIR $TMP_DIR
PROBLEM=github_issue_summarization_problem
USR_DIR=./github
rm -rf $DATA_DIR/*
# Generate data
# This can take a while depending on the size of the data
t2t-datagen \
  --t2t_usr_dir=$USR_DIR \
  --problem=$PROBLEM \
  --data_dir=$DATA_DIR \
  --tmp_dir=$TMP_DIR

# Copy to GCS where it can be used by distributed training
gsutil cp -r ${DATA_DIR} gs://${BUCKET_NAME}/${DATA_DIR}
```

## Build and push docker image for distributed training

The [github](tensor2tensor/github) directory contains a Dockerfile to build the docker image
required for distributed training.

```
cd tensor2tensor/github
docker build . -t gcr.io/${GCR_REGISTRY}/tensor2tensor-training-cpu:latest \
  --build-arg BASE_IMAGE=gcr.io/kubeflow-images-public/tensorflow-1.7.0-notebook-cpu:latest
gcloud docker -- push gcr.io/${GCR_REGISTRY}/tensor2tensor-training-cpu:latest
```

## Launch distributed training

This directory contains a ksonnet app([ks-kubeflow](./ks-kubeflow)) to deploy the TFJob.


Set the appropriate params for the tfjob component

```commandline
ks param set tensor2tensor namespace ${NAMESPACE}

ks param set tensor2tensor dataDir "gs://${BUCKET_NAME}/${DATA_DIR}"
ks param set tensor2tensor outputGCSPath "gs://${BUCKET_NAME}/training"
# The image pushed in the previous step
ks param set tensor2tensor cpuImage "gcr.io/${GCR_REGISTRY}/tensor2tensor-training:latest"
ks param set tensor2tensor workers 3
ks param set tensor2tensor trainSteps 5000

```

Deploy the app:

```commandline
ks apply ${KF_ENV} -c tensor2tensor
```

You can view the logs of the master job using:

```commandline
kubectl logs -f \
  $(kubectl get pods -ltf_job_name=tensor2tensor,job_type=MASTER -o=jsonpath='{.items[0].metadata.name}')
```

For information on:
- [Training the model](02_training_the_model.md)
- [Training the model using TFJob](02_training_the_model_tfjob.md)

*Next*: [Serving the model](03_serving_the_model.md)

*Back*: [Setup a kubeflow cluster](01_setup_a_kubeflow_cluster.md)
