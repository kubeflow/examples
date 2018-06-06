# Semantic Code Search

This demo implements End-to-End Semantic Code Search on Kubeflow. It is based on the public
Github Dataset hosted on BigQuery.

## Prerequisites

* Python 2.7 (with `pip`)
* Python 3.6+ (with `pip3`)
* Python `virtualenv`

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

## 2. Function Summarizer

This part generates a model to summarize functions into docstrings using the data generated in previous
step. It uses `tensor2tensor`.

* Install dependencies
```
(venv3) $ pip install -r summarizer/requirements.txt
```

* Generate `TFRecords` for training
```
(venv3) $ t2t-datagen --t2t_usr_dir=summarizer/gh_function_summarizer --problem=github_function_summarizer \
                      --data_dir=~/data --tmp_dir=/tmp
```

* Train transduction model using `Tranformer Networks` and a base hyper-parameters set
```
(venv3) $ t2t-trainer --t2t_usr_dir=summarizer/gh_function_summarizer --problem=github_function_summarizer \
                      --data_dir=~/data --model=transformer --hparams_set=transformer_base --output_dir=~/train
```

# Acknowledgements

This project derives from [hamelsmu/code_search](https://github.com/hamelsmu/code_search).