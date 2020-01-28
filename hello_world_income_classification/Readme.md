## Getting started example with Kubeflow: Income classification using Linear classifier

This is an end-to-end Kubeflow example with a Linear classifier model trained to predict whether the income of an individual is above 50K.
The goal of this project is to serve as a simple example and a reference project for users starting their Kubeflow journey.

This example mimics a users journey in Kubeflow so that the development workflow on Kubeflow is clear, and equips users to build more complex projects and examples.

Hence, this example takes an opinionated approach and excludes complexities arising from enhancements, and we'll be discussing more of these potential enhancements throughout this example.

  
Here's the table of contents:
-  [Getting started with Kubeflow](#mnist-on-kubeflow)

    -  [Prerequisites](#prerequisites)

    -  [Install Kubeflow](#install-kubeflow)

-  [Spinning a Jupyter Notebook](#spin-up-a-notebook)

-  [Developing the model](#developing-a-linear-classifier-model)

-  [Distributed training using TfJob](#distributed-training-using-tfjob)

    -  [Using Local storage](#local-storage)

-  [Monitoring](#monitoring)

-  [Tensorboard](#tensorboard)

    -  [Local storage](#local-storage-1)

-  [Hyper parameter tuning with Katib](#hyper-parameter-tuning-with-katib)


-  [Serving the model](#serving-the-model)

    -  [Local storage](#local-storage-2)

-  [Web Front End](#web-front-end)

    -  [Connecting via port forwarding](#connecting-via-port-forwarding)

-  [Connecting the components and automating the workflow using pipelines](#pipelines)

## Install Kubeflow 
While Kubeflow can be installed on any Kubernetes deployment in any enviroment, we'll go with our opinioated approach and take the easiest option: using the Google Cloud deployer.

Using the quick form,  you quickly set up with Kubeflow after just filling out some information, this even takes care of deploying Kubernetes, so you need not worry about having a Kubernetes cluster to start with.

If you want to install Kubeflow in other environments, find the intructions here from the [official docs](https://www.kubeflow.org/docs/started/getting-started/).

Let's follow these simple steps and get Kubeflow installed:
-  Create a new Google cloud project.

- Enable billing.

- Enable APIs

-  Fill the form 

- You're set

## Spin up a notebook


## Developing a linear classifier model
- Problem statement


- The dataset


- Building the model

**Step 1:** 
Download a small subset into the Kubeflow notebook 
   
**Step 2:** 
List all feature columns 
List the continous value features and categorical features separately.

**Step 3:** 
Create input pipeline

**Step 4:** 
Create feature columns 

**Step 5**
Create the Linear Regression model 

**Step 6**
Train the model 

**Step 7:** 
Evaluate the model

## Distributed training using TfJob


 

