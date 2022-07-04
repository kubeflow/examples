# Objective

This example is based on the Titanic Kaggle competition. The objective of this exercise is to use machine learning to create a model that predicts which passengers survived the Titanic shipwreck.

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2 and x86-64 and ARM based system which includes all Intel and AMD based CPU's and M1/M2 series Macbooks

## Step 1: Setup Kubeflow as a Service

- If you haven’t already, sign up (https://www.arrikto.com/kubeflow-as-a-service/)
- Deploy Kubeflow

## Step 2: Launch a Notebook Server

- Default should work

## Step 3: Clone the Project Repo to Your Notebook

- (Kubeflow as a Service) Open up a terminal in the Notebook Server and git clone the `kubeflow/examples` repository
```
git clone https://github.com/ajinkya933/examples-1/
```

## Step 4: Setup DockerHub and Docker

- If you haven’t already, sign up (https://hub.docker.com/) for DockerHub
- If you haven’t already, install Docker Desktop (https://www.docker.com/products/docker-desktop/) locally OR install the Docker command line utility (https://docs.docker.com/get-docker/) and enter `sudo docker login` command in your terminal and log into Docker with your your DockerHub username and password 

## Step 5: Setup Kaggle

- If you haven’t already done so, sign up (https://www.kaggle.com/) for Kaggle
- (On Kaggle) Generate an API token (https://www.kaggle.com/docs/api)
- (Kubeflow as a Service) Create a Kubernetes secret
```
kubectl create secret generic kaggle-secret --from-literal=KAGGLE_USERNAME=<username> --from-literal=KAGGLE_KEY=<api_token> 
```

## Step 6: Install Git

- (Locally) If you don’t have it already, install Git

## Step 7: Clone the Project Repo Locally

- (Locally) Git clone the kubeflow/examples repository
```
git clone https://github.com/ajinkya933/examples-1/
```


