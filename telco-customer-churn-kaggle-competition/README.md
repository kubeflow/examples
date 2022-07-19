# Objective
In this example we are going to convert this generic [notebook](https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/telco-customer-churn-orig.ipynb) 
based on the [Telco Customer Churn Prediction](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) competition into a Kubeflow pipeline.

The objective of this task is to analyze customer behavior in the telecommunication sector and to predict their tendency to churn.

# Testing Environment

Environment:
| Name        | version           | 
| ------------- |:-------------:|
| Kubeflow      | v1.4   |
| kfp           | 1.8.11 |
| kubeflow-kale | 0.6.0  |
| pip           | 21.3.1 |


## Section 1: Overview

1. Vanilla KFP Pipeline: Kubeflow lightweight component method

   To get started, visit the Kubeflow Pipelines [documentation](https://www.kubeflow.org/docs/components/pipelines/sdk/) 
   to get acquainted with what pipelines are, its components, pipeline metrics and how to pass data between components in a pipeline. 
   There are different ways to build out a pipeline component as mentioned [here](https://www.kubeflow.org/docs/components/pipelines/sdk/build-pipeline/#building-pipeline-components). 
   In the following example, we are going to use the lightweight python functions based components for building our Kubeflow pipeline.

2. Kale KFP Pipeline

   To get started, visit Kale's [documentation](https://docs.arrikto.com/user/kale/index.html) to get acquainted with the 
   Kale user interface (UI) from a Jupyter Notebook, [notebook cell annotation](https://docs.arrikto.com/user/kale/jupyterlab/annotate.html) 
   and how to create a machine learning pipeline using Kale.
   In the following example, we are going to use the Kale JupyterLab Extension to building our Kubeflow pipeline.

## Section 2: Vanilla KFP Pipeline

### Kubeflow lightweight component method
Here, a python function is created to carry out a certain task and the python function is passed inside a kfp component method [`create_component_from_func`](https://kubeflow-pipelines.readthedocs.io/en/latest/source/kfp.components.html#kfp.components.create_component_from_func). 

The different components used in this example are:

- Load data
- Transform data
- Feature Engineering
- Catboost Modeling
- Xgboost Modeling
- Lightgbm Modeling
- Ensembling

## Kubeflow pipelines
A Kubeflow pipeline connects all components together, to create a directed acyclic graph (DAG). The kfp [`dsl.pipeline`](https://www.kubeflow.org/docs/components/pipelines/sdk/sdk-overview/) decorator was used to create a pipeline function. 
The kfp component method [`InputPath`](https://kubeflow-pipelines.readthedocs.io/en/latest/source/kfp.components.html#kfp.components.InputPath) and [`OutputPath`](https://kubeflow-pipelines.readthedocs.io/en/latest/source/kfp.components.html#kfp.components.OutputPath) was used to pass data between components in the pipeline. 

Finally, the  [`create_run_from_pipeline_func`](https://kubeflow-pipelines.readthedocs.io/en/stable/source/kfp.client.html) from the KFP SDK Client was used to submit pipeline directly from pipeline function

## To create pipeline using Vanilla KFP
   
1. Open your Kubeflow Cluster, create a Notebook Server and connect to it.

2. Clone this repo and navigate to this directory.
3. Open the [telco-customer-churn-kfp](https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/telco-customer-churn-kfp.ipynb) notebook 
4. Run the telco-customer-churn-kfp notebook from start to finish
5. View run details immediately after submitting pipeline.

### View Pipeline

<p align=center>
<img src="https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/images/telco-kfp-pipeline.PNG?raw=true" alt="telco-kfp-pipeline"/>
</p>

### View Pipeline Visualization

<p align=center>
<img src="https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/images/telco-kfp-pipeline-visualization.PNG?raw=true" alt="telco-kfp-pipeline-visualization"/>
</p>

## Section 2: Kale KFP Pipeline

To create pipeline using the Kale JupyterLab extension


1. Clone GitHub repo and navigate to this directory

2. Launch the [telco-customer-churn-kale](https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/telco-customer-churn-kale.ipynb) Notebook

3. Install the requirements.txt file. After installation, restart kernel.

4. Enable the Kale extension in JupyterLab 

5. The notebook's cells are automatically annotated with Kale tags

   To fully understand the different Kale tags available, visit Kale [documentation](https://docs.arrikto.com/user/kale/jupyterlab/cell-types.html?highlight=pipeline%20metrics#annotate-pipeline-step-cells)
   
   The following Kale tags were used in this example:

   * Imports
   * Pipeline Step
   * Skip Cell
   
   With the use of Kale tags we define the following:

   * Pipeline parameters are assigned using the "pipeline parameters" tag
   * The necessary libraries that need to be used throughout the Pipeline are passed through the "imports" tag
   * Notebook cells are assigned to specific Pipeline components (download data, load data, etc.) using the "pipeline step" tag
   * Cell dependencies are defined between the different pipeline steps with the "depends on" flag
   * Pipeline metrics are assigned using the "pipeline metrics" tag
   
   The pipeline steps created in this example:

   * Load data
   * Transform data
   * Feature Engineering
   * Catboost Modeling
   * Xgboost Modeling
   * Lightgbm Modeling
   * Ensembling

6. Compile and run the Notebook by hitting the "Compile & Run" in Kale's left panel

<p align=center>
<img src="https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/images/kale-deployment-panel.PNG?raw=true" alt="kale-deployment-panel"/>
</p>

### View Pipeline

View Pipeline by clicking "View" in Kale's left panel

<p align=center>
<img src="https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/images/view-pipeline.PNG?raw=true" alt="view-pipeline
"/>
</p>


<p align=center>
<img src="https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/images/telco-kale-pipeline.PNG?raw=true" alt="telco-kale-pipeline"/>
</p>

### View Pipeline Visualization

<p align=center>
<img src="https://github.com/kubeflow/examples/blob/master/telco-customer-churn-kaggle-competition/images/telco-kale-pipeline-visualization.PNG?raw=true" alt="telco-kale-pipeline-visualization"/>
</p>
