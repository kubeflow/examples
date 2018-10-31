# Regression and classification

_**Linear regression and multi-class classification**_

### Overview

This sample provides a generic way to process CSV files to train models.
This code supports:
 
 - Linear regression
 - Binary classification (Regression)
 - Multi-class classification

### Tensorflow model

* The sample provided uses the high level `tf.contrib.learn.Estimator` API. 
  This API is great for fast iteration, and quickly adapting models to your own 
  datasets without major code overhauls.
  **Version:** ```Tensorflow Version: 1.10```

## Datasets

You can bring your own dataset (BYOD), as long as first column is the
target column.

The following examples are for well know datasets:

### Classification

The [Iris Dataset](https://archive.ics.uci.edu/ml/datasets/iris) that this sample
uses for training is hosted by the [UC Irvine Machine Learning
Repository](https://archive.ics.uci.edu/ml/datasets/). We have also hosted the data
on Google Cloud Storage:

 * Training file is [`train.csv`](https://storage.googleapis.com/cloud-samples-data/ml-engine/iris/classification/train.csv)
 * Evaluation file is [`evaluate.csv`](https://storage.googleapis.com/cloud-samples-data/ml-engine/iris/classification/evaluate.csv)

The dataset contains 4 different features:

1.  Sepal Length.
2.  Sepal Width.
3.  Petal Length.
4.  Petal Width.


### Regression

We'll use the
[Boston Housing dataset](https://www.cs.toronto.edu/~delve/data/boston/bostonDetail.html)
This dataset contains information collected by the U.S Census Service concerning
housing in the area of Boston Mass. It was obtained from the StatLib archive
(http://lib.stat.cmu.edu/datasets/boston), and has been used extensively
throughout the literature to benchmark algorithms. The dataset
is small in size with only 506 cases.

The dataset contains 13 different features:

1.  Per capita crime rate.
2.  The proportion of residential land zoned for lots over 25,000 square feet.
3.  The proportion of non-retail business acres per town.
4.  Charles River dummy variable (= 1 if tract bounds river; 0 otherwise).
5.  Nitric oxides concentration (parts per 10 million).
6.  The average number of rooms per dwelling.
7.  The proportion of owner-occupied units built before 1940.
8.  Weighted distances to five Boston employment centers.
9.  Index of accessibility to radial highways.
10. Full-value property-tax rate per $10,000.
11. Pupil-teacher ratio by town.
12. 1000 * (Bk - 0.63) ** 2 where Bk is the proportion of Black people by town.
13. Percentage lower status of the population.


## How to satisfy project structure requirements

The basic project structure will look something like this:

```shell
.
├── Dockerfile
├── README.md
├── setup.py
├── requirements.txt
└── src
    ├── __init__.py
    ├── model.py
    ├── preprocessor.py     
    └── task.py
```

## Virtual environment

Virtual environments are strongly suggested, but not required. Installing this
sample's dependencies in a new virtual environment allows you to run the sample
without changing global python packages on your system.

There are two options for the virtual environments:

*   Install [Virtual](https://virtualenv.pypa.io/en/stable/) env
    *   Create virtual environment `virtualenv mnist`
    *   Activate env `source mnist/bin/activate`
*   Install [Miniconda](https://conda.io/miniconda.html)
    *   Create conda environment `conda create --name mnist python=2.7`
    *   Activate env `source activate mnist`

## Install dependencies

*   Install the python dependencies. `pip install --upgrade -r requirements.txt`

### Get your training data

If you want to use local files directly, you can use the following commands:

```shell
mkdir data && cd data
curl -O https://storage.googleapis.com/cloud-samples-data/ml-engine/iris/classification/train.csv
cd ..
```

### Upload the data to a Google Cloud Storage bucket

This module works by using resources available in the cloud, so the training
data needs to be placed in such a resource. For this example, we'll use [Google
Cloud Storage], but it's possible to use other resources like [BigQuery]. Make a
bucket (names must be globally unique) and place the data in there:

```shell
gsutil mb gs://your-bucket-name
gsutil cp -r data/train.csv gs://your-bucket-name/train.csv
```

### Project configuration file: `setup.py`

The `setup.py` file is run on the to install
packages/dependencies and set a few options.

```python
from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
  requirements = [l.strip('\n') for l in f if
                  l.strip('\n') and not l.startswith('#')]

setup(
  name='linear_learner',
  version='0.1',
  install_requires=requirements,
  packages=find_packages(),
  include_package_data=True,
  description='ML pipelines'
)
```

## Classification

## Run the model locally

You can run the Tensorflow code locally to validate your project.

Use local training file.

```
export IRIS_DATA=../data/classification/
export JOB_NAME="iris_$(date +%Y%m%d_%H%M%S)"
export JOB_DIR=/tmp/$JOB_NAME
export TRAIN_FILE=$IRIS_DATA/train.csv
export EVAL_FILE=$IRIS_DATA/evaluate.csv
```

Use remote file located in GCS.

```
export BUCKET_NAME=your-bucket-name
export JOB_NAME="iris_$(date +%Y%m%d_%H%M%S)"
export JOB_DIR=/tmp/$JOB_NAME
export TRAIN_FILE=gs://cloud-samples-data//ml-engine/iris/classification/train.csv
export EVAL_FILE=gs://cloud-samples-data//ml-engine/iris/classification/evaluate.csv
export REGION=us-central1
```

Run the model with python (local)

```
python task.py --training_data_path=$TRAIN_FILE --validation_data_path=$EVAL_FILE --job_dir=$JOB_DIR --model_type=classification --learning_rate=0.001
```


## Regression

## Run the model locally

You can run the Tensorflow code locally to validate your project.

Use local training file.

```
export BOSTON_DATA=../data/regression/
export JOB_NAME="boston_$(date +%Y%m%d_%H%M%S)"
export JOB_DIR=/tmp/$JOB_NAME
export TRAIN_FILE=$BOSTON_DATA/train.csv
export EVAL_FILE=$BOSTON_DATA/evaluate.csv
```

Use remote file located in GCS.

```
export BUCKET_NAME=your-bucket-name
export JOB_NAME="boston_$(date +%Y%m%d_%H%M%S)"
export JOB_DIR=/tmp/$JOB_NAME
export TRAIN_FILE=gs://cloud-samples-data/ml-engine/boston/regression/train.csv
export EVAL_FILE=gs://cloud-samples-data/ml-engine/boston/regression/evaluate.csv
export REGION=us-central1
```

Run the model with python (local)

```
python task.py --training_data_path=$TRAIN_FILE --validation_data_path=$EVAL_FILE --job_dir=$JOB_DIR --model_type=regression --learning_rate=0.001
```



## Monitor training with TensorBoard

If Tensorboard appears blank, try refreshing after 10 minutes.

```
tensorboard --logdir=$JOB_DIR
```

