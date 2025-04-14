# Objective

This example is based on the "Heart Disease Exploratory data analysis" from Kaggle (https://www.kaggle.com/code/georgyzubkov/heart-disease-exploratory-data-analysis).
The objective of this exercise is to use different types of Machine Learning models to predict cardiovascular disease risk.

We will use Kubeflow Pipelines with the Kaggle API to download the original "Indicators of Heart Disease" dataset (https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease)
and perform training in parallel of the different Machine Learning models, to finally analyze the performance results.

## Prerequisites

- _Kaggle API token_: this can be retrieved from the [personal Kaggle account settings](https://www.kaggle.com/settings/account).

## Environment

This pipeline was tested using Kubeflow Pipelines 2.0.5 and KFP sdk 2.6.0.

## Launch a Notebook Server

- Use defaults

## Clone the Project Repo to Your Notebook

- In Kubeflow Notebook Server, git clone the `kubeflow/examples` repository.
```
git clone https://github.com/kubeflow/examples
```
- Navigate in `framingham-cvd-risk`.
- You can leverage `requirements-ipynb.txt` for the required Python dependencies if not already installed in your Notebook image.
- You can use `original-heart-disease-exploratory-data-analysis.ipynb` to replicate the exploratory data analysis from Kaggle.
- You will need to maintain the variables at the top of the Notebook with your Kaggle API Token in order to download the DataSet.

## Generate a KFP Pipeline yaml File

- In an environment with Python available, run `pip install -r requirements-kfp.txt`.
- Then produce the pipeline YAML file using KFP `python pipeline.py`.
- You can also leverage the already made-available file `pipeline.py.yaml` in this repo.

## Create a Pipeline

- Within the Kubeflow Central Dashboard, navigate to the `Pipelines` > `+Upload Pipeline` button
- Name the pipeline
- Click on Upload a file, `Choose file` button
- Upload the local `pipeline.py.yaml` file
- Click Create

## Create Kaggle Secret

- Retrieve the Kaggle `username` and `key`, see [prerequisites](#prerequisites) section for more details.
- Create secret running:
```bash
kubectl create secret generic kaggle-api \
    --from-literal=KAGGLE_KEY="<replace-with-your-key>" \
    --from-literal=KAGGLE_USERNAME='<replace-with-your-username>'
```

> _NOTE_: The secret name must be `kaggle-api` as expected by the [pipeline definition](./pipeline.py).

## Create a Run

- Click on `+Create Run` button in the view from the previous step
- Associate to your desired Experiment as needed or leave defaults
- You will be navigated to the just created Run instance to view the progression on the runtime execution graph

## Pipeline Run results

![Run results](/kfp-run-screenshot1.png)
![Run results](/kfp-run-screenshot2.png)

## Based on:

- Apache-2.0 https://www.kaggle.com/code/georgyzubkov/heart-disease-exploratory-data-analysis
- CC0: Public Domain https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease
