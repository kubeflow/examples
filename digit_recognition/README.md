# Objective
Here we convert the https://www.kaggle.com/competitions/digit-recognizer code to kfp-pipeline 
The objective of this task is to correctly identify digits from a dataset of tens of thousands of handwritten images.

# Testing environment
Data Scientists on this project:
| Name        | version           | 
| ------------- |:-------------:|
| Kubeflow      | v1     |
| kfp           | 1.8.11 |
| kubeflow-kale | 0.6.0  |
| pip           | 21.3.1 |


Kfp version used for testing can be installed as `pip install kfp==1.8.11`  

# Section 1: kfp pipeline

## kubeflow lightweight component method
Here, a python function is created to carry out a certain task and the python function is passed inside kfp component method`create_component_from_func`. 


## Kubeflow pipelines
Kubeflow pipelines connect each components according to how they were passed and creates a pipeline. The kfp `dsl.pipeline` method was used to create a pipeline function. The kkfp component method `InputPath` and `OutputPath` was used to pass data amongst component. 

Finally, the  `create_run_from_pipeline_func` was used to submit pipeline directly from pipeline function

## To create pipeline on kfp
1. Navigate to `data` directory, download compressed kaggle data and put your `training.zip` and `test.zip` data in the data folder.
   Also download `sample_sumbission.csv` and store in the data folder 
   
2. Open your setup kubeflow cluster and create a notebook server and connect to it.

3. Clone this repo and navigate to this directory

4. run the kfp-digit-recognizer notebook from start to finish

5. View run details immediately after submitting pipeline.

# Section 2: kale pipeline

## To create pipeline on kale
1. install requirements file
2. enable kale extension in jupyter lab
3. the notebooks cells are annotated with kale tags 
    
    With the kale tags: 
    1. pipeline parameters are assigned. 
    2. the necessary libraries to be used through out the pipelines are passed  
    3. notebook cells are assigned to specific pipeline components (download data, load data, etc.) as pipeline steps.
    4. dependencies are defined between the different pipeline steps
   
4. compile and run notebook
