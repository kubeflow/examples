# Semantic Code Search

This demo implements End-to-End Semantic Code Search on Kubeflow. It is based on the public
Github Dataset hosted on BigQuery.

## Prerequisites

* Python 2.7 (with `pip`)
* Python 3.6+ (with `pip3`)
* Python `virtualenv`
* Docker

**NOTE**: `Apache Beam` lacks `Python3` support and hence the multiple versions needed.

## Google Cloud Setup

* Install [`gcloud`](https://cloud.google.com/sdk/gcloud/) CLI

* Setup Application Default Credentials 
```
$ gcloud auth application-default login
```

* Enable Dataflow via Command Line (or use the Google Cloud Console)
```
$ gcloud services enable dataflow.googleapis.com
```

* Create a Google Cloud Project and Google Storage Bucket.

See [Google Cloud Docs](https://cloud.google.com/docs/) for more.

## Python Environment Setup

This demo needs multiple Python versions and `virtualenv` is an easy way to
create isolated environments.

```
$ virtualenv -p $(which python2) venv2 && virtualenv -p $(which python3) venv3 
```

This creates two environments, `venv2` and `venv3` for `Python2` and `Python3` respectively.

To use either of the environments,

```
$ source venv2/bin/activate | source venv3/bin/activate # Pick one
```

See [Virtualenv Docs](https://virtualenv.pypa.io/en/stable/) for more. 

# Pipeline

## 1. Data Pre-processing

This step takes in the public Github dataset and generates function and docstring token pairs.
Results are saved back into a BigQuery table.

* Install dependencies
```
(venv2) $ pip install -r preprocess/requirements.txt
```

* Execute the `Dataflow` job
```
$ python preprocess/scripts/process_github_archive.py -i files/select_github_archive.sql \
         -o code_search:function_docstrings -p kubeflow-dev -j process-github-archive \
         --storage-bucket gs://kubeflow-dev --machine-type n1-highcpu-32 --num-workers 16 \
         --max-num-workers 16
```

## 2. Model Training

A `Dockerfile` based on Tensorflow is provided along which has all the dependencies for this part of the pipeline. 
By default, it is based off Tensorflow CPU 1.8.0 for `Python3` but can be overridden in the Docker image build using
the following command

```
$ export BUILD_IMAGE_TAG=my-new-tag # (optional) to change built image tag
$ export BASE_IMAGE_TAG=1.8.0-gpu-py3 # (optional) for GPU base image
$ ./language_task/build_image.sh
```

### 2.1 Function Summarizer

This part generates a model to summarize functions into docstrings using the data generated in previous
step. It uses `tensor2tensor`.

* Generate `TFRecords` for training
```
$ export MOUNT_DATA_DIR=/path/to/data/folder # (optional) mount a local data directory
$ export DOCKER_ENTRYPOINT=t2t-datagen # (required)
$ ./language_task/run.sh --problem=github_function_summarizer
```

* Train transduction model using `Tranformer Networks` and a base hyper-parameters set
```
$ export MOUNT_DATA_DIR=/path/to/data/folder # (optional) mount a local data directory
$ export DOCKER_ENTRYPOINT=t2t-trainer # (required)
$ ./language_task/run.sh --problem=github_function_summarizer --model=transformer --hparams_set=transformer_base
```

### 2.2 Docstrings Language Model

This part trains a language model based on the docstrings in the dataset and uses `tensor2tensor`

* Generate `TFRecords` for training
```
$ export MOUNT_DATA_DIR=/path/to/data/folder # (optional) mount a local data directory
$ export DOCKER_ENTRYPOINT=t2t-datagen # (required)
$ ./language_task/run.sh --problem=github_docstring_language_model
```

* Train language model using `Tranformer Networks` and a custom hyper-parameters set
```
$ export MOUNT_DATA_DIR=/path/to/data/folder # (optional) mount a local data directory
$ export MOUNT_OUTPUT_DIR=/path/to/output/folder # (optional) mount a local output directory
$ export DOCKER_ENTRYPOINT=t2t-trainer # (required)
$ ./language_task/run.sh --problem=github_docstring_language_model --model=transformer --hparams_set=transformer_gh_lm
```

# Acknowledgements

This project derives from [hamelsmu/code_search](https://github.com/hamelsmu/code_search).
