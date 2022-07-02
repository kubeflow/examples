# Objective

This example is based on the Titanic OpenVaccine competition. The objective of this exercise is to develop models and design rules for RNA degradation.

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2 and x86-64 based system which includes all Intel and AMD based CPU's. 

## Step 1: Setup Kubeflow as a Service

- If you haven’t already, sign up (https://www.arrikto.com/kubeflow-as-a-service/)
- Deploy Kubeflow

## Step 2: Launch a Notebook Server

- Bump memory to 2GB and vCPUs to 2

## Step 3: Clone the Project Repo to Your Notebook

- (Kubeflow as a Service) Open up a terminal in the Notebook Server and git clone the `kubeflow/examples` repository
```
git clone https://github.com/kubeflow/examples

```
## Step 4: Setup DockerHub and Docker

- If you haven’t already, sign up (https://hub.docker.com/) for DockerHub 
- If you haven’t already, install Docker Desktop locally (https://www.docker.com/products/docker-desktop/) OR install the Docker command line utility (https://docs.docker.com/get-docker/) and enter `sudo docker login` command in your terminal and log into Docker with your your DockerHub username and password 


## Step 5: Setup Kaggle

- If you haven’t already done so, sign up (https://www.kaggle.com/) for Kaggle
- (On Kaggle) Generate an API token (https://www.kaggle.com/docs/api)
- (Kubeflow as a Service) Create a Kubernetes secret

```
kubectl create secret generic kaggle-secret --from-literal=KAGGLE_USERNAME=<username> --from-literal=KAGGLE_KEY=<api_token> 
```

## Step 6: Install Git

- (Locally) If you don’t have it already, install Git (https://github.com/git-guides/install-git)

## Step 7: Clone the Project Repo Locally

- (Locally) Git clone the `kubeflow/examples` repository
```
git clone https://github.com/kubeflow/examples
```

## Step 8: Create a PodDefault Resource

- (Kubeflow as a Service) Navigate to the `openvaccine-kaggle-competition` directory
- Create a `resource.yaml` file

![image2](https://user-images.githubusercontent.com/17012391/177001253-3e525eb6-3415-428c-a52b-11803326af6b.png)

- Apply created resource using: kubectl apply -f resource.yaml

## Step 9: Explore the load-data directory

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/load-data` directory
- Open up the `load.py` file
- Note the code in this file that will perform the actions required in the “load-data” pipeline step

<img width="209" alt="image7" src="https://user-images.githubusercontent.com/17012391/177001311-efbee116-5a7a-498e-9d3a-6b50f192db97.png">

## Step 10: Build the `load-data` Docker Image

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/load-data` directory
- Build the Docker image if locally you are using arm64 (Apple M1)

```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```

## Step 11: Push the load-data Docker Image to DockerHub

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/load-data` directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```

## Step 12: Explore the `preprocess-data` directory

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/preprocess-data` directory
- Open up the `preprocess.py` file
- Note the code in this file that will perform the actions required in the “preprocess” pipeline step

<img width="209" alt="image5" src="https://user-images.githubusercontent.com/17012391/177001608-bc82e3ea-7581-4de9-bd29-2d0fc410b817.png">


## Step 13: Explore the `preprocess-data` directory
- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/preprocess-data` directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```





















## Frequently encountered errors:
While running the pipeline as mentioned above you may come across this error:
![kaggle-secret-error-01](https://user-images.githubusercontent.com/17012391/175290593-aac58d80-0d9f-47bd-bd20-46e6f5207210.PNG)

errorlog:

```
kaggle.rest.ApiException: (403)
Reason: Forbidden
HTTP response headers: HTTPHeaderDict({'Content-Type': 'application/json', 'Date': 'Thu, 23 Jun 2022 11:31:18 GMT', 'Access-Control-Allow-Credentials': 'true', 'Set-Cookie': 'ka_sessionid=6817a347c75399a531148e19cad0aaeb; max-age=2626560; path=/, GCLB=CIGths3--ebbUg; path=/; HttpOnly', 'Transfer-Encoding': 'chunked', 'Vary': 
HTTP response body: b'{"code":403,"message":"You must accept this competition\\u0027s rules before you\\u0027ll be able to download files."}'

```
This error occours for two reasons:
- Your Kaggle account is not verified with your phone number.
- Rules for this specific competitions are not accepted.

Lets accept Rules of competition 
![rules](https://user-images.githubusercontent.com/17012391/175306310-10808262-07ce-4952-8fb0-3b7754e9fb46.png)

Click on "I Understand and Accept". After this you will be prompted to verify your account using your phone number:
![kaggle-secret-error-03](https://user-images.githubusercontent.com/17012391/175291608-daad1a47-119a-4e47-b48b-4f878d65ddd7.PNG)

Add your phone number and Kaggle will send the code to your number, enter this code and verify your account. ( Note: pipeline wont run if your Kaggle account is not verified )

## Success
After the kaggle account is verified pipeline run is successful we will get the following:
<img width="1244" alt="Screenshot 2022-06-06 at 3 00 51 PM" src="https://user-images.githubusercontent.com/17012391/172135040-50d6e9f3-d156-4e95-9b9f-492e99108d82.png">
