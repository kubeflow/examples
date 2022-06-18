# Objective

This example is based on the Telco Customer Churn competition. 

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2 and x86-64 based system which includes all Intel and AMD based CPU's. ARM based systems are not supported.

## Prerequisites for Building the Kubeflow Pipeline

### Kubeflow

It is assumed that you have Kubeflow installed. 

### Docker

Docker is used to create an image to run each component in the pipeline.

### Kubeflow Pipelines

Kubeflow Pipelines connects each Docker-based component to create a pipeline. Each pipeline is a reproducible workflow wherein we pass input arguments and run the entire workflow.


# Build the Train and Evaluate images with Docker

Kubeflow relies on Docker images to create pipelines. These images are pushed to a Docker container registry, from which Kubeflow accesses them. For the purposes of this how-to we are going to use Docker Hub as our registry.

## Step 1: Log into Docker

Start by creating a Docker account on DockerHub (https://hub.docker.com/). After signing up, Install Docker https://docs.docker.com/get-docker/ and enter  `docker login`  command on your terminal and enter your docker-hub username and password to log into Docker.



## Step 2: Build the datapreprocessing image

Next, on your docker enviornment go to terminal and navigate to the pipeline-components/preprocess/ directory and build the evaluate Docker image using:
```
$ cd pipeline-components/preprocess/
$ docker build -t <docker_username>/<docker_imagename>:<tag> .
```
For example:
```
$ docker build -t hubdocker76/telco-preprocess:v2 .
```
After building push the image using:
```
$ docker push hubdocker76/telco-preprocess:v2
```
## Step 4: Build the Train image

Next, on your docker enviornment go to terminal and navigate to the pipeline-components/train/ directory and build the evaluate Docker image using:
```
$ cd pipeline-components/train/
$ docker build -t <docker_username>/<docker_imagename>:<tag> .
```

For example:
```
$ docker build -t hubdocker76/telco-train:v13 .
```
After building push the image using:
```
$ docker push hubdocker76/telco-train:v13
```
## Step 5: Build the Test image

Next, on your docker enviornment go to terminal and navigate to the pipeline-components/test/ directory and build the evaluate Docker image using:
```
$ cd pipeline-components/test/
$ docker build -t <docker_username>/<docker_imagename>:<tag> .
```
For example:
```
$ docker build -t hubdocker76/telco-test:v6 .
```
After building push the image using:
```
$ docker push hubdocker76/telco-test:v6
```


## Kubeflow Pipeline

As a needed step we create a virtual enviornment, that contains all components we need to convert our python code to yaml file.

Steps to build a python virtual enviornment:

Step a) Update pip
```
python3 -m pip install --upgrade pip
```

Step b) Install virtualenv
```
sudo pip3 install virtualenv
```

Step c) Check the installed version of venv
```
virtualenv --version
```

Step d) Name your virtual enviornment as kfp
```
virtualenv kfp
```

Step e) Activate your venv.
```
source kfp/bin/activate
```

After this virtual environment will get activated. Now in our activated venv we need to install following packages:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y git python3-pip

python3 -m pip install  kfp==1.1.2
```

After installing packages create the yaml file

Inside venv point your terminal to a path which contains our kfp file to build pipeline (facial-keypoints-detection-kfp.py) and run these commands:
```
$ python3 telco-kaggle-competition-kfp.py
```
…this will generate a yaml file:
```
telco-kaggle-competition-kfp.yaml
```

## Run the Kubeflow Pipeline

This `telco-kaggle-competition-kfp.yaml` file can then be uploaded to Kubeflow Pipelines UI from which you can create a Pipeline Run. The same yaml file will also be generated if we run the blue-book-for-bulldozers-kfp.ipynb notebook in the Notebook Server UI.


Upload file :
<img width="1292" alt="Screenshot 2022-05-23 at 10 08 40 PM" src="https://user-images.githubusercontent.com/17012391/169867378-17394de5-c4d7-49e6-bd41-adf02291976d.png">





And then Start the Run.
<img width="1322" alt="Screenshot 2022-05-23 at 10 10 49 PM" src="https://user-images.githubusercontent.com/17012391/169867569-19f61116-64b8-4bc6-af93-d06488d5d66b.png">


## Success
After the pipeline run is successful we will get the following:

