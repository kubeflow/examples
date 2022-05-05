# Objective

This example is based on the Facial Keypoints Detection Kaggle competition. The objective of this exercise is to predict keypoint positions on face images.

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2

## Prerequisites for Building the Kubeflow Pipeline

### Kubeflow

It is assumed that you have Kubeflow installed. 

### Docker

Docker is used to create an image to run each component in the pipeline.

### Kubeflow Pipelines

Kubeflow Pipelines connects each Docker-based component to create a pipeline. Each pipeline is a reproducible workflow wherein we pass input arguments and run the entire workflow.

# Apply Kubernetes secret
We will use Kaggle API to get input data from Kaggle to Kubeflow pipeline. In order to get this data securly we need to apply a Kubernetes secret

Step1: Create secret
```
kubectl create secret generic kaggle-secret --from-literal=KAGGLE_USERNAME=<username> --from-literal=KAGGLE_KEY=<api_token> 
```
Step2: create a file named `secret.yaml` as follows:
```
apiVersion: "kubeflow.org/v1alpha1"
kind: PodDefault
metadata:
  name: kaggle-access
spec:
 selector:
  matchLabels:
    kaggle-secret: "true"
 desc: "kaggle-access"
 volumeMounts:
 - name: secret-volume
   mountPath: /secret/kaggle
 volumes:
 - name: secret-volume
   secret:
    secretName: kaggle-secret
```
Apply this yaml
```
kubectl apply -f secret.yaml 
```


# Build the Train and Evaluate images with Docker

Kubeflow relies on Docker images to create pipelines. These images are pushed to a Docker container registry, from which Kubeflow accesses them. For the purposes of this how-to we are going to use Docker Hub as our registry.

## Step 1: Log into Docker

Start by creating a Docker account on DockerHub. After signing up, log into Docker using your username and password at the terminal.

## Step 2: Build the Train image

Navigate to the pipeline-components/train/ directory and build the train Docker image using:
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
For example:
```
docker build -t hubdocker76/demotrain:v8 .
```
## Step 3: Build the Evaluate image

Next, navigate to the pipeline-components/eval/ directory and build the evaluate Docker image using:
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
For example:
```
docker build -t hubdocker76/demoeval:v3 .
```
## Kubeflow Pipeline

Create the yaml file

Run:
```
python3 facial-keypoints-detection-kfp.py 
```
…this will generate a yaml file. 

Run the Kubeflow Pipeline

This file can then be uploaded to Kubeflow Pipelines UI from which you can create a Pipeline Run. The same yaml file will also be generated if we run the facial-keypoints-detection-kfp.ipynb notebook in the Notebook Server UI.

# Kubeflow Pipeline with Kale

To run this pipeline using the Kale JupyterLab extension, upload the `facial-keypoints-detection-kale.ipynb` file to your Kubeflow deployment where Kale is enabled. Once uploaded create a folder named `my_data` and paste `test.zip` and `training.zip` from Kaggle into this folder, click “compile and run” to create a pipeline run.
