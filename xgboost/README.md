# Ames housing value prediction using XGBoost on Kubeflow

In this example we will demonstrate how to use Kubeflow with XGBoost. We will do a detailed
walk-through of how to implement, train and serve the model. You will be able to run the exact same workload on-prem and/or on any cloud provider. We will be using [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine/) to show how the end-to-end workflow runs on [Google Cloud Platform](https://cloud.google.com/). 

# Pre-requisites

As a part of running this setup on Google Cloud Platform, make sure you have enabled the [Google
Kubernetes Engine](https://cloud.google.com/kubernetes-engine/). In addition to that you will need to install
[Docker](https://docs.docker.com/install/) and [gcloud](https://cloud.google.com/sdk/downloads). Note that this setup can run on-prem and on any cloud provider, but here we will demonstrate GCP cloud option. 

# Steps
 * [Kubeflow Setup](#kubeflow-setup)
 * [Data Preparation](#data-preparation)
 * [Dockerfile](#dockerfile)
 * [Model Training](#model-training)
 * [Model Export](#model-export)
 * [Model Serving Locally](#model-serving)
 * [Deploying Model to Kubernetes Cluster](#deploying-the-model-to-kubernetes-cluster)

## Kubeflow Setup
In this part you will setup Kubeflow on an existing Kubernetes cluster. Checkout the Kubeflow [setup guide](https://github.com/kubeflow/kubeflow#setup). 

## Data Preparation
You can download the dataset from the [Kaggle competition](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data). In order to make it convenient we have uploaded the dataset on Github here [xgboost/ames_dataset](ames_dataset). 

## Dockerfile
We have attached a Dockerfile with this repo which you can use to create a
docker image. We have also uploaded the image to gcr.io, which you can use to
directly download the image.

```
IMAGE_NAME=ames-housing
VERSION=v1
```

Let's create a docker image from our Dockerfile

```
docker build -t ${IMAGE_NAME}:${VERSION} .
```

Once the above command is successful you should be able to see the docker
images on your local machine `docker images`. Next we will upload the image to
[Google Container Registry](https://cloud.google.com/container-registry/)

```
PROJECT_ID=`gcloud config get-value project`
gcloud docker -- push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${VERSION}
```

## Model Training

Once you have performed `docker build` you should be able to see the images by running `docker images`. Get the `IMAGE_ID` for the image `seldonio/housingserve` and run the training by issuing the following command 

```
docker run -v /tmp/ames/:/model/ames -it $IMAGE_ID --train-input examples/xgboost/ames_dataset/train.csv \
                                                   --model-file /model/ames/housing.dat \
                                                   --learning-rate 0.1 \
                                                   --n-estimators 30000 \
                                                   --early-stopping-rounds 50
```

In the above command we have mounted the container filesystem `/model/ames` to the host filesystem `/tmp/ames` so that the model is available on localhost. Check the local host filesystem for the trained XGBoost model

```
ls -lh /tmp/ames/housing.dat
```

## Model Export
The model is exported at location `/tmp/ames/housing.dat`. We will use [Seldon Core](https://github.com/SeldonIO/seldon-core/) to serve the model asset. In order to make the model servable we have created `xgboost/seldon_serve` with the following assets

 * `HousingServe.py`
 * `housing.dat`
 * `requirements.txt`

## Model Serving
We are going to use [seldon-core](https://github.com/SeldonIO/seldon-core/) to serve the model. [HousingServe.py](seldon_serve/HousingServe.py) contains the code to serve the model. Run the following command to create a microservice 

```
docker run -v $(pwd):/seldon_serve seldonio/core-python-wrapper:0.7 /seldon_serve HousingServe 0.1 seldonio
```

Let's build the seldon-core microservice image. You can find seldon core model wrapping details [here](https://github.com/SeldonIO/seldon-core/blob/master/docs/wrappers/python.md).

```
cd build
./build_image.sh
```

You should see the docker image locally `seldonio/housingserve` which can be run locally to serve the model. 

```
docker run -p 5000:5000 seldonio/housingserve:0.1
```

Now you are ready to send requests on `localhost:5000` [TODO: JSON API Request]

## Deploying the model to Kubernetes Cluster
TODO
