# Objective

This example is based on the Titanic Kaggle competition (https://www.kaggle.com/c/titanic). The objective of this exercise is to use machine learning to create a model that predicts which passengers survived the Titanic shipwreck.

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
git clone https://github.com/kubeflow/examples
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
git clone https://github.com/kubeflow/examples
```
## Step 8: Create a `PodDefault` Resource

- (Kubeflow as a Service) Navigate to the `titanic-kaggle-competition` directory
- Create a `resource.yaml` file

resource.yaml:
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
<img width="662" alt="Screenshot 2022-07-04 at 4 56 41 PM" src="https://user-images.githubusercontent.com/17012391/177145496-e46bfe4e-baf3-48cf-b3ac-52fc90a88888.png">

- Apply the resource.yaml file: `kubectl apply -f resource.yaml`

## Step 9: Explore the pre-process directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/pre-process` directory
- Open up the `preprocess.py` file
- Note the code in this file that will perform the actions required in the “preprocess-data” pipeline step

<img width="288" alt="Screenshot 2022-07-04 at 5 00 01 PM" src="https://user-images.githubusercontent.com/17012391/177145992-eaa2abe0-2fb3-4ec8-aa64-2f5c3ec9e6e0.png">

## Step 10: Build the preprocess-data Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/pre-process` directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
## Step 11: Push the preprocess-data Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/load-data` directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 12: Explore the featureengineering directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/featureengineering` directory
- Open up the `featureengg.py` file
- Note the code in this file that will perform the actions required in the “featureengineering” pipeline step

<img width="320" alt="Screenshot 2022-07-04 at 5 02 50 PM" src="https://user-images.githubusercontent.com/17012391/177146398-8354e2d6-6300-4398-a3d8-27f3931c48b3.png">

## Step 13: Build the featureengineering Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/featureengineering` directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
## Step 14: Push the featureengineering Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/featureengineering`  directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```

## Step 15: Explore the decisiontree directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/decisiontree` directory
- Open up the `decisiontree.py` file
- Note the code in this file that will perform the actions required in the “decision-tree” pipeline step

<img width="270" alt="Screenshot 2022-07-04 at 5 05 43 PM" src="https://user-images.githubusercontent.com/17012391/177146813-0f9b90bd-bf4f-4738-b9e9-4f8cceaf9ff9.png">

## Step 16: Build the decisiontree Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/decisiontree`  directory
Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```

## Step 17: Push the decisiontree Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/decisiontree` directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 18: Explore the logisticregression directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/logisticregression` directory
- Open up the `regression.py` file
- Note the code in this file that will perform the actions required in the “regression” pipeline step

<img width="293" alt="Screenshot 2022-07-04 at 5 08 11 PM" src="https://user-images.githubusercontent.com/17012391/177147179-ac6d0ece-2f4d-4a38-bc80-a04bf95b8c21.png">

## Step 19: Build the regression Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/logisticregression`  directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
## Step 20: Push the regression Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/logisticregression`  directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 21: Explore the naivebayes directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/naivebayes` directory
- Open up the `naivebayes.py` file
Note the code in this file that will perform the actions required in the “bayes” pipeline step
<img width="300" alt="Screenshot 2022-07-04 at 5 10 36 PM" src="https://user-images.githubusercontent.com/17012391/177147549-ef53079e-16e6-4c8b-989e-59c8b3ef9846.png">

## Step 22: Build the naivebayes Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/naivebayes`  directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
## Step 23: Push the naivebayes Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/naivebayes`  directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 24: Explore the randomforest directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/randomforest` directory
- Open up the `randomforest.py` file
- Note the code in this file that will perform the actions required in the “random-forest” pipeline step


<img width="278" alt="Screenshot 2022-07-04 at 5 12 54 PM" src="https://user-images.githubusercontent.com/17012391/177147918-c88f1ef1-29a8-489b-8e9d-c16d902be28a.png">

## Step 25: Build the random-forest Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/randomforest`   directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```

## Step 26: Push the random-forest Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/randomforest`   directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 27: Explore the svm directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/svm` directory
- Open up the `svm.py` file
- Note the code in this file that will perform the actions required in the “svm” pipeline step

<img width="333" alt="Screenshot 2022-07-04 at 5 15 23 PM" src="https://user-images.githubusercontent.com/17012391/177148267-810c39af-2037-483f-a5fd-89f1e9901e8a.png">

## Step 28: Build the svm Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/svm`   directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```
## Step 29: Push the svm Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/svm`   directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 30: Explore the results directory

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/results` directory
- Open up the `result.py` file
- Note the code in this file that will perform the actions required in the “results” pipeline step

<img width="291" alt="Screenshot 2022-07-04 at 5 18 34 PM" src="https://user-images.githubusercontent.com/17012391/177148827-c6688435-1f3d-40e7-950c-bc7cfda0a7e8.png">

## Step 31: Build the results Docker Image

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/results`   directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```

## Step 32: Push the results Docker Image to DockerHub

- (Locally) Navigate to the `titanic-kaggle-competition/pipeline-components/results`   directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```

## Step 33: Modify the titanic-kfp.py file

- (Kubeflow as a Service) Navigate to the `titanic-kaggle-competition` directory
- Update the `titanic-kfp.py` with accurate Docker Image inputs
```
   return dsl.ContainerOp(
        name = 'Preprocess Data', 
        image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='featureengineering',
        image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='regression',
        image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='bayes',
  image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='random_forest',
  image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='decision_tree',
  image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='svm',
  image = '<dockerhub username>/<image name>:<tag>',

—-----

    return dsl.ContainerOp(
        name='results',
  image = '<dockerhub username>/<image name>:<tag>',
```

## Step 34: Generate a KFP Pipeline yaml File

- (Kubeflow as a Service) Navigate to the `titanic-kaggle-competition` directory
Build a python virtual environment:

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
```
python3 titanic-kaggle-competition-kfp.py
```

<img width="300" alt="Screenshot 2022-07-04 at 5 27 37 PM" src="https://user-images.githubusercontent.com/17012391/177150179-9146d84b-bd3f-4d94-8e22-5d30ef0911a4.png">


Download the `titanic-kaggle-competition-kfp.yaml` file that was created to your local `titanic-kaggle-competition` directory. 

## Step 35: Create an Experiment

- (Kubeflow as a Service) Within the Kubeflow Central Dashboard, navigate to the Experiments (KFP) > Create Experiment view
- Name the experiment and click Next
- Click on Experiments (KFP) to view the experiment you just created

## Step 36: Create a Pipeline

- (Kubeflow as a Service) Within the Kubeflow Central Dashboard, navigate to the Pipelines > +Upload Pipeline view
- Name the pipeline
- Click on Upload a file
- Upload the local `titanic-kaggle-competition-kfp.yaml` file
- Click Create


## Step 37: Create a Run

- (Kubeflow as a Service) Click on Create Run in the view from the previous step
- Choose the experiment we created in Step 35
- Click Start
- Click on the run name to view the runtime execution graph


![image10](https://user-images.githubusercontent.com/17012391/177150882-3c8abf80-2d6e-4467-9b11-7824d3909e35.png)


## Troubleshooting Tips:
While running the pipeline as mentioned above you may come across this error:
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

A solution to this is please verify your Kaggle account using your phone number and accept the rules for this specific competition, untill these two steps are satisfied pipeline wont accquire data from Kaggle API and it wont run.
