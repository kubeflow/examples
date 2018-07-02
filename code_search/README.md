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
$ python preprocess/scripts/process_github_archive.py -p kubeflow-dev -j process-github-archive \
  --storage-bucket gs://kubeflow-examples/t2t-code-search -o code_search:function_docstrings \
  --machine-type n1-highcpu-32 --num-workers 16 --max-num-workers 16
```

## 2. Model Training

A `Dockerfile` based on Tensorflow is provided along which has all the dependencies for this part of the pipeline. 
By default, it is based off Tensorflow CPU 1.8.0 for `Python3` but can be overridden in the Docker image build.
This script builds and pushes the docker image to Google Container Registry.

### 2.1 Build & Push images to GCR

**NOTE**: The images can be pushed to any registry of choice but rest of the 

* Authenticate with GCR
```
$ gcloud auth configure-docker
```

* Build and push the image
```
$ PROJECT=my-project ./build_image.sh
```
and a GPU image
```
$ GPU=1 PROJECT=my-project ./build_image.sh
```

See [GCR Pushing and Pulling Images](https://cloud.google.com/container-registry/docs/pushing-and-pulling) for more.


### 2.2 Train Locally

**WARNING**: The container might run out of memory and be killed.

#### 2.2.1 Function Summarizer

* Train transduction model using `Tranformer Networks` and a base hyper-parameters set
```
$ export MOUNT_DATA_DIR=/path/to/data/folder
$ export MOUNT_OUTPUT_DIR=/path/to/output/folder
$ docker run --rm -it -v ${MOUNT_DATA_DIR}:/data -v ${MOUNT_OUTPUT_DIR}:/output ${BUILD_IMAGE_TAG} \
    --generate_data --problem=github_function_docstring --data_dir=/data --output_dir=/output \
    --model=similarity_transformer --hparams_set=transformer_base
```

### 2.2 Train on Kubeflow

* Setup secrets for access permissions Google Cloud Storage and Google Container Registry
```shell
$ PROJECT=my-project ./create_secrets.sh
```

**NOTE**: Use `create_secrets.sh -d` to remove any side-effects of the above step.

# Acknowledgements

This project derives from [hamelsmu/code_search](https://github.com/hamelsmu/code_search).
