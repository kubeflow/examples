# Objective
Here we convert the https://www.kaggle.com/competitions/digit-recognizer code to a Kubeflow pipeline 
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
A Kubeflow pipelines connects all components together, to create a directed acyclic graph (DAG). The kfp `dsl.pipeline` method was used to create a pipeline function. The kfp component method `InputPath` and `OutputPath` was used to pass data amongst component. 

Finally, the  `create_run_from_pipeline_func` was used to submit pipeline directly from pipeline function

## To create pipeline on KFP
   
1. Open your Kubeflow Cluster, create a Notebook Server and connect to it.

2. Clone this repo and navigate to this directory

3. Navigate to `data` directory, download the compressed kaggle data using this [link](https://www.kaggle.com/competitions/digit-recognizer/data), store the `training.zip`, `test.zip` and `sample_sumbission.csv` files in the data folder

4. Run the digit-recognizer-kfp notebook from start to finish

5. View run details immediately after submitting pipeline.

### View Pipeline

<p>
<img src="https://github.com/josepholaide/examples/blob/master/digit-recognition-kaggle-competition/images/kfp-pipeline.PNG?raw=true" alt="kubeflow pipeline" width="600" height="700"/>
 </p>


# Section 2: Kale Pipeline

To create pipeline using the Kale JupyterLab extension


1. Clone GitHub repo and navigate to this directory

2. Install the requirements.txt file

3. Launch the digit-recognizer-kale.ipynb Notebook

4. Enable the Kale extension in JupyterLab   

5. The notebook's cells are automatically annotated with Kale tags

   With the use of Kale tags we define the following:

   * Pipeline parameters are assigned using the "pipeline parameters" tag
   * The necessary libraries that need to be used throughout the Pipeline are passed through the "imports" tag
   * Notebook cells are assigned to specific Pipeline components (download data, load data, etc.) using the "pipeline step" tag
   * Cell dependencies are defined between the different pipeline steps with the "depends on" flag

6. Compile and run Notebook using Kale

### View Pipeline

<p>
<img src="https://github.com/josepholaide/examples/blob/master/digit-recognition-kaggle-competition/images/kale-pipeline.PNG?raw=true" alt="kubeflow pipeline" width="600" height="700"/>
 </p>
