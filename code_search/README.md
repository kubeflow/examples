# Semantic Code Search

This demo implements End-to-End Semantic Code Search on Kubeflow. It is based on the public
Github Dataset hosted on BigQuery.

## Setup

### Prerequisites

* Python 2.7 (with `pip`)
* Python `virtualenv`
* Node
* Docker
* Ksonnet

**NOTE**: `Apache Beam` lacks `Python3` support and hence the version requirement.

### Google Cloud Setup

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

* Authenticate with Google Container Registry to push Docker images
```
$ gcloud auth configure-docker
```

See [Google Cloud Docs](https://cloud.google.com/docs/) for more.

### Python Environment Setup

This demo needs multiple Python versions and `virtualenv` is an easy way to
create isolated environments.

```
$ virtualenv -p $(which python2) env2.7 
```

This creates a `env2.7` environment folder.

To use the environment,

```
$ source env2.7/bin/activate
```

See [Virtualenv Docs](https://virtualenv.pypa.io/en/stable/) for more. 

**NOTE**: The `env2.7` environment must be activated for all steps now onwards.

### Python Dependencies

To install dependencies, run the following commands

```
(env2.7) $ pip install https://github.com/activatedgeek/batch-predict/tarball/fix-value-provider
(env2.7) $ pip install src/
```

This will install everything needed to run the demo code.

### Node Dependencies

```
$ pushd ui && npm i && popd
```

### Build and Push Docker Images

The `docker` directory contains Dockerfiles for each target application with its own `build.sh`. This is needed
to run the training jobs in Kubeflow cluster.

To build the Docker image for training jobs

```
$ ./docker/t2t/build.sh
```

To build the Docker image for Code Search UI

```
$ ./docker/ui/build.sh
```

Optionally, to push these images to GCR, one must export the `PROJECT=<my project name>` environment variable
and use the appropriate build script.

See [GCR Pushing and Pulling Images](https://cloud.google.com/container-registry/docs/pushing-and-pulling) for more.

# Pipeline

## 1. Data Pre-processing

This step takes in the public Github dataset and generates function and docstring token pairs.
Results are saved back into a BigQuery table. It is done via a `Dataflow` job.

```
(env2.7) $ export GCS_DIR=gs://kubeflow-examples/t2t-code-search
(env2.7) $ code-search-preprocess -r DataflowRunner -o code_search:function_docstrings \
              -p kubeflow-dev -j process-github-archive --storage-bucket ${GCS_DIR} \
              --machine-type n1-highcpu-32 --num-workers 16 --max-num-workers 16
```

## 2. Model Training

We use `tensor2tensor` to train our model.

```
(env2.7) $ t2t-trainer --generate_data --problem=github_function_docstring --model=similarity_transformer --hparams_set=transformer_tiny \
                      --data_dir=${GCS_DIR}/data --output_dir=${GCS_DIR}/output \
                      --train_steps=100 --eval_steps=10 \
                      --t2t_usr_dir=src/code_search/t2t
```

A `Dockerfile` based on Tensorflow is provided along which has all the dependencies for this part of the pipeline. 
By default, it is based off Tensorflow CPU 1.8.0 for `Python3` but can be overridden in the Docker image build.
This script builds and pushes the docker image to Google Container Registry.

## 3. Model Export

We use `t2t-exporter` to export our trained model above into the TensorFlow `SavedModel` format.

```
(env2.7) $ t2t-exporter --problem=github_function_docstring --model=similarity_transformer --hparams_set=transformer_tiny \
                      --data_dir=${GCS_DIR}/data --output_dir=${GCS_DIR}/output \
                      --t2t_usr_dir=src/code_search/t2t
```

## 4. Batch Prediction for Code Embeddings

We run another `Dataflow` pipeline to use the exported model above and get a high-dimensional embedding of each of
our code example. Specify the model version (which is a UNIX timestamp) from the output directory. This should be the name of 
a folder at path `${GCS_DIR}/output/export/Servo`

```
(env2.7) $ export MODEL_VERSION=<put_unix_timestamp_here>
```

Now, start the job,

```
(env2.7) $ export SAVED_MODEL_DIR=${GCS_DIR}/output/export/Servo/${MODEL_VERSION}
(env2.7) $ code-search-predict -r DataflowRunner --problem=github_function_docstring -i "${GCS_DIR}/data/*.csv" \
              --data-dir "${GCS_DIR}/data" --saved-model-dir "${SAVED_MODEL_DIR}"
              -p kubeflow-dev -j batch-predict-github-archive --storage-bucket ${GCS_DIR} \
              --machine-type n1-highcpu-32 --num-workers 16 --max-num-workers 16
```

## 5. Create an NMSLib Index

Using the above embeddings, we will now create an NMSLib index which will serve as our search index for
new incoming queries.


```
(env2.7) $ export INDEX_FILE=  # TODO(sanyamkapoor): Add the index file
(env2.7) $ nmslib-create --data-file=${EMBEDDINGS_FILE} --index-file=${INDEX_FILE}
```


## 6. Run a TensorFlow Serving container

This will start a TF Serving container using the model export above and export it at port 8501.

```
$ docker run --rm -p8501:8501 gcr.io/kubeflow-images-public/tensorflow-serving-1.8 tensorflow_model_server \
             --rest_api_port=8501 --model_name=t2t_code_search --model_base_path=${GCS_DIR}/output/export/Servo
```

## 7. Serve the Search Engine

We will now serve the search engine via a simple REST interface

```
(env2.7) $ nmslib-serve --serving-url=http://localhost:8501/v1/models/t2t_code_search:predict \
                        --problem=github_function_docstring --data-dir=${GCS_DIR}/data --index-file=${INDEX_FILE}
```

## 8. Serve the UI

This will serve as the graphical wrapper on top of the REST search engine started in the previous step.

```
$ pushd ui && npm run build && popd
$ serve -s ui/build
```

# Pipeline on Kubeflow

TODO

# Acknowledgements

This project derives from [hamelsmu/code_search](https://github.com/hamelsmu/code_search).
