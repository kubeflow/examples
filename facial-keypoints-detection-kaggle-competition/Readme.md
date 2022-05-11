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

# Apply PodDefault resource

## Step 1: Generate Kaggle API token
The input data needed to run this tutorial is been pulled from Kaggle . In order to pull the data we need to create a Kaggle account , user needs to register with his email and password and create a Kaggle username. 

Once we have successfully registered our Kaggle account. Now, we have to access the API Token . API access is needed to pull data from Kaggle , to get the API access go to you Kaggle profile and click on your profile picture on the top right  we will see this option: 

<img width="358" alt="Account" src="https://user-images.githubusercontent.com/17012391/167830480-334e2586-5df1-4cf4-be79-cfcfda5048ac.png">

Select “Account” from the menu.

Scroll down to the “API” section and click “Create New API Token” :
<img width="926" alt="Screenshot 2022-05-10 at 1 03 34 PM" src="https://user-images.githubusercontent.com/17012391/167830572-a7412306-f0cb-4f1f-8f93-28253a127202.png">


This will download a file ‘kaggle.json’ with the following contents :
```
username	“My username”
key	“My key”
```
Now, substitute your “username” for `<username>` and your “key” for  `<api_token>` and create a Kubernetes secret using:  
```
kubectl create secret generic kaggle-secret --from-literal=KAGGLE_USERNAME=<username> --from-literal=KAGGLE_KEY=<api_token> 
```

  
## Step2: Create a PodDefault resource

We need a way to inject common data (env vars, volumes) to pods. In Kubeflow we use PodDefault resource which serves this usecase (reference: https://github.com/kubeflow/kubeflow/blob/master/components/admission-webhook/README.md).  Using the PodDefault resource we can attach a secret to our data pulling step container which downloads data using Kaggle API. We create and apply PodDefault resource as follows :

Create a `resource.yaml` file with the following code:

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
  
Apply the yaml with the following command:
```
kubectl apply -f resource.yaml 
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

To run this pipeline using the Kale JupyterLab extension, upload the `facial-keypoints-detection-kale.ipynb` file to your Kubeflow deployment where Kale is enabled. Once uploaded run the cell annotated with `skip` tag which downloads the data using Kaggle API (use `<username>` and `<api_token>`  as highlighted in `Apply PodDefault resource` step to get get data using Kaggle API) and save the download data to `my_data` folder.   click “compile and run” to create a pipeline run.
