# Semantic Code Search

End-to-End Semantic Code Search on Kubeflow

## Prerequisites

* Python 2.7 (with `pip`)
* Python `virtualenv`

**NOTE**: This project uses Google Cloud Dataflow which only supports Python 2.7.

## Setup

* Setup Python Virtual Environment
```
$ virtualenv venv
$ source venv/bin/activate
```

* Install [`gcloud`](https://cloud.google.com/sdk/gcloud/) CLI

* Setup Application Default Credentials 
```
$ gcloud auth application-default login
```

* Enable Dataflow via Command Line (or use the Google Cloud Console)
```
$ gcloud services enable dataflow.googleapis.com
```

* Build and install package
```
$ python setup.py build install
```

# Pipeline

## Pre-process Python Source files from Github to Google BigQuery

A sample execution looks like:

```
$ python scripts/process_github_archive.py -i files/select_github_archive.sql -o code_search:function_docstrings -p kubeflow-dev 
                        -j process-github-archive --storage-bucket gs://kubeflow-dev
```

**NOTE**: Make sure the Project and Google Storage Bucket is created.

# Acknowledgements

This project derives from [hamelsmu/code_search](https://github.com/hamelsmu/code_search).
