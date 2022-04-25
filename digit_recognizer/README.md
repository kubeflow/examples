# Objective
Here we convert the https://www.kaggle.com/competitions/digit-recognizer code to kfp-pipeline 
The objective of this task is tois to correctly identify digits from a dataset of tens of thousands of handwritten images.

# Testing environment
Data Scientists on this project:
| Name        | version           | 
| ------------- |:-------------:|
| Kubeflow      | v1     |
| kfp           | 1.8.11 |


Kfp version used for testing can be installed as `pip install kfp==1.8.11`  

# Components used

## kubeflow lightweight component method
Here, a python function is created to carry out a certain task and the python function is passed inside kfp component method`create_component_from_func`. 


## Kubeflow pipelines
Kubeflow pipelines connect each components according to how they were passed and creates a pipeline. The kfp `dsl.pipeline` method was used to create a pipeline function. The kkfp component method `InputPath` and `OutputPath` was used to pass data amongst component. 

Finally, the  `create_run_from_pipeline_func` was used to submit pipeline directly from pipeline function

## To create pipeline
Navigate to `train` directory, create a folder named `my_data` and put your `training.zip` and `test.zip` data from Kaggle repo in this folder and build docker image using :
