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
Navigate to `pipeline-components/train/` and build train docker image using :
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
In my case this is:
```
docker build -t hubdocker76/demotrain:v4 .
```

## Build evaluate image
Navigate to `pipeline-components/eval/` directory and build docker image using :
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
In my case this is:
```
docker build -t hubdocker76/demoeval:v2 .
```
# Vanilla Kubeflow pipelines

Run `python3 facial-keypoints-detection-kfp.py` this will generate a yaml file. which we can upload to Kubeflow pipelines UI and create a Run from it. The same yaml file can also be generated if we run `facial-keypoints-detection-kfp.ipynb` notebook

# Sample pipeline to run on Kubeflow
Run `python3 facial-keypoints-detection-kfp.py` this will generate yaml file. Please upload this pipeline on Kubeflow and start a Run.

# Kale
Upload `facial-keypoints-detection-kale.ipynb` file to Kubeflow where Kale is enabled and compile and run the notebook. 

