# Named Entity Recognition with Kubeflow and Keras 

This example demonstrates how you can use Kubeflow to train and deploy a Keras model with a custom prediction routine. 

## Goals

* Demonstrate how to use Keras only models
* Demonstrate how to train a Named Entity Recognition model
* Demonstrate how to deploy a Keras model to AI Platform
* Demonstrate how to use a custom prediction routine
* Demonstrate how to use Kubeflow metrics
* Demonstrate how to use Kubeflow visualizations 

## What is Named Entity Recognition
Named Entity Recognition is a word classification problem, which extract data called entities from text.

![solution](documentation/files/solution.png)

### Usage

1. [Setup Kubeflow and clone repository](documentation/step-1-setup.md)
1. [Build the pipeline components](documentation/step-2-build-components.md)
1. [Upload the dataset](documentation/step-3-upload-dataset.md)
1. [Custom prediction routine](documentation/step-4-custom-prediction-routine.md)
1. [Run the pipeline](documentation/step-5-run-pipeline.md)
1. [Monitor the training](documentation/step-6-monitor-training.md)
1. [Predict](documentation/step-7-predictions.md)

### Model 
Bi-LSTM (Bidirectional long Short term memory) a type of RNN (Recurrent Neural Network).





