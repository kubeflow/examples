# Objective

This example is based on the Titanic OpenVaccine competition (https://www.kaggle.com/c/stanford-covid-vaccine). The objective of this exercise is to develop models and design rules for RNA degradation.

## Environment

This pipeline was tested using Kubeflow 1.4 and kfp 1.1.2 and x86-64 and ARM based system which includes all Intel and AMD based CPU's and M1/M2 series Macbooks. 

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

![image2](https://user-images.githubusercontent.com/17012391/177001253-3e525eb6-3415-428c-a52b-11803326af6b.png)

- Apply created resource using: `kubectl apply -f resource.yaml`

## Step 9: Explore the `load-data` directory

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

## Step 11: Push the `load-data` Docker Image to DockerHub

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

## Step 14: Push the `preprocess-data` Docker Image to DockerHub

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/preprocess-data` directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```

## Step 15: Explore the `model-training` directory

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/model-training` directory
- Open up the `model.py` file
- Note the code in this file that will perform the actions required in the “train” pipeline step

![image4](https://user-images.githubusercontent.com/17012391/177001740-a63f190c-284e-4328-ba01-17dbdbe61cee.png)

## Step 16: Build the `model-training` Docker Image

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/model-training` directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```

## Step 17: Push the `model-training` Docker Image to DockerHub

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/model-training` directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```

## Step 18: Explore the `model-evaluation` directory

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/model-evaluation` directory
- Open up the `eval.py` file
- Note the code in this file that will perform the actions required in the “test” pipeline step

![image1](https://user-images.githubusercontent.com/17012391/177001951-1f7b13b9-adea-48c1-89a7-d8dc67214133.png)


## Step 19: Build the `model-evaluation` Docker Image

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/model-evaluation` directory
- Build the Docker image if locally you are using arm64 (Apple M1)
```
docker build --platform=linux/amd64 -t <docker_username>/<docker_imagename>:<tag>-amd64 . 
```
- OR build the Docker image if locally you are using amd64
```
docker build -t <docker_username>/<docker_imagename>:<tag> .
```

## Step 20: Push the `model-evaluation` Docker Image to DockerHub

- (Locally) Navigate to the `openvaccine-kaggle-competition/pipeline-components/model-evaluation` directory
- Push the Docker image if locally you are using arm64 (Apple M1)
```
docker push <docker_username>/<docker_imagename>:<tag>-amd64 
```
- OR build the Docker image if locally you are using amd64
```
docker push <docker_username>/<docker_imagename>:<tag>
```
## Step 21: Modify the openvaccine-kaggle-competiton-kfp.py file

- (Kubeflow as a Service) Navigate to the `openvaccine-kaggle-competition` directory
- Update the `openvaccine-kaggle-competiton-kfp.py` with accurate Docker Image inputs

```
   return dsl.ContainerOp(
        name = 'load-data', 
        image = '<dockerhub username>/<image name>:<tag>',

—-----

def GetMsg(comp1):
    return dsl.ContainerOp(
        name = 'preprocess',
        image = '<dockerhub username>/<image name>:<tag>',

—-----

def Train(comp2, trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength):
    return dsl.ContainerOp(
        name = 'train',
        image = '<dockerhub username>/<image name>:<tag>',

—-----

def Eval(comp1, trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength):
    return dsl.ContainerOp(
        name = 'Evaluate',
  image = '<dockerhub username>/<image name>:<tag>',
```

## Step 22: Generate a KFP Pipeline yaml File

- (Locally) Navigate to the `openvaccine-kaggle-competition` directory and delete the existing `openvaccine-kaggle-competition-kfp.yaml` file
- (Kubeflow as a Service) Navigate to the openvaccine-kaggle-competition directory

Build a python virtual environment :


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

Inside venv point your terminal to a path which contains our kfp file to build pipeline (openvaccine-kaggle-competition-kfp.py) and run these commands to generate a `yaml` file for the Pipeline:

```
python3 openvaccine-kaggle-competition-kfp.py
```
<img width="492" alt="image3" src="https://user-images.githubusercontent.com/17012391/177002110-5c0bdfc3-f9cc-453d-84b4-0107f506d54d.png">

Download the `openvaccine-kaggle-competition-kfp.yaml` file that was created to your local `openvaccine-kaggle-competition` directory

## Step 23: Create an Experiment

- (Kubeflow as a Service) Within the Kubeflow Central Dashboard, navigate to the Experiments (KFP) > Create Experiment view
- Name the experiment and click Next
- Click on Experiments (KFP) to view the experiment you just created

## Step 24: Create a Pipeline


- (Kubeflow as a Service) Within the Kubeflow Central Dashboard, navigate to the Pipelines > +Upload Pipeline view
- Name the pipeline
- Click on Upload a file
- Upload the local `openvaccine-kaggle-competition-kfp.yaml` file
- Click Create

## Step 25: Create a Run

- (Kubeflow as a Service) Click on Create Run in the view from the previous step
- Choose the experiment we created in Step 23
- Input your desired run parameters. For example:
```
TRIAL = 1
EPOCHS = 2
BATCH_SIZE = 64
EMBED_DIM = 100
HIDDEN_DIM = 128
DROPOUT = .2
SP_DROPOUT = .3
TRAIN_SEQUENCE_LENGTH = 107
```
- Click Start
- Click on the run name to view the runtime execution graph




![image6](https://user-images.githubusercontent.com/17012391/177002214-8258e3fa-e669-43cc-979d-70c1059f6aae.png)




















## Troubleshooting Tips:
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
