# Objective
Here we convert the https://www.kaggle.com/competitions/jpx-tokyo-stock-exchange-prediction code to a Kubeflow pipeline 
The objective of this task is to correctly identify digits from a dataset of tens of thousands of handwritten images.

# Testing Environment

Environment:
| Name        | version           | 
| ------------- |:-------------:|
| Kubeflow      | v1.4   |
| kfp           | 1.8.11 |
| kubeflow-kale | 0.6.0  |
| pip           | 21.3.1 |


The KFP version used for testing can be installed as `pip install kfp==1.8.11`  

# Section 1: KFP Pipeline

## Kubeflow lightweight component method
Here, a python function is created to carry out a certain task and the python function is passed inside a kfp component method`create_component_from_func`. 


## Kubeflow pipelines
A Kubeflow pipelines connects all components together, to create a directed acyclic graph (DAG). The kfp `dsl.pipeline` method was used to create a pipeline function. 
The kfp component method `InputPath` and `OutputPath` was used to pass data amongst component. 
