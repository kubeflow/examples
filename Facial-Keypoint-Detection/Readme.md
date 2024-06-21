# Objective
Here we convert the https://www.kaggle.com/competitions/facial-keypoints-detection code to kfp-pipeline 
The objective of this task is to predict keypoint positions on face images

# Testing enviornment
The pipeline is tested on `Kubeflow 1.4` and `kfp 1.1.2` , it should be compatible with previous releases of Kubeflow . kfp version used for testing is 1.1.2 which can be installed as `pip install kfp==1.1.2`  

# Components used

## Docker
Docker is used to create an enviornment to run each component.

## Kubeflow pipelines
Kubeflow pipelines connect each docker component and create a pipeline. Each Kubeflow pipeline is reproducable workflow wherein we pass input arguments and run entire workflow.  

# Docker
We start with creating a docker account on dockerhub (https://hub.docker.com/). We signup with our individual email. After signup is compelete login to docker using your username and password using the command `docker login` on your terminal

## Build train image
Navigate to `train` directory, create a folder named `my_data` and put your `training.zip` and `test.zip` data from Kaggle repo in this folder and build docker image using :
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
In my case this is:
```
docker build -t hubdocker76/demotrain:v1 .
```

## Build evaluate image
Navigate to eval directory and build docker image using :
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
In my case this is:
```
docker build -t hubdocker76/demoeval:v2 .
```
# Kubeflow pipelines

Go to generate-pipeline and run `python3 my_pipeline.py` this will generate a yaml file. which we can upload to Kubeflow pipelines UI and create a Run from it.

# Sample pipeline to run on Kubeflow
Navigate to directory `geneate-pipeline` and run `python3 my_pipeline.py` this will generate yaml file. I have named this yaml as `face_pipeline_01.yaml`. Please upload this pipeline on Kubeflow and start a Run.
