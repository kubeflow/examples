# Objective
Here we convert the https://www.kaggle.com/competitions/jpx-tokyo-stock-exchange-prediction code to a Kubeflow pipeline 
The objective of this task is to correctly model real future returns of around 2,000 stocks. The stocks are ranked from highest 
to lowest expected returns and they are evaluated on the difference in returns between the top and bottom 200 stocks.

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

Finally, the  `create_run_from_pipeline_func` was used to submit pipeline directly from pipeline function

## To create pipeline on KFP
   
1. Open your Kubeflow Cluster, create a Notebook Server and connect to it.

2. Clone this repo and navigate to this directory

3. Download JPX dataset using Kaggle's API. To do this, do the following:
   
   * Login to Kaggle and click on your user profile picture.
   * Click on ‘Account’.
   * Under ‘Account’, navigate to the ‘API’ section.
   * Click ‘Create New API token’.
   * After creating a new API token, a kaggle.json file is automatically downloaded, 
      and the json file contains the ‘api-key’ and ‘username’ needed to download the dataset.

4. Open the digit-recognizer-kfp notebook and pass the ‘api-key’ and ‘username’ in the following cells.
   
 * enter username
   
<p>
<img src="https://github.com/josepholaide/examples/blob/master/jpx-tokyo-stock-exchange-kaggle-competition/images/enter-username.PNG?raw=true" alt="enter username" width="700" height="300"/>
</p>
 
   * enter api key

<p>
<img src="https://github.com/josepholaide/examples/blob/master/jpx-tokyo-stock-exchange-kaggle-competition/images/enter-api-key.PNG?raw=true" alt="enter api key" width="700" height="250"/>
</p> 
 
5. Run the digit-recognizer-kfp notebook from start to finish

6. View run details immediately after submitting pipeline.

### View Pipeline

<p>
<img src="https://github.com/josepholaide/examples/blob/master/jpx-tokyo-stock-exchange-kaggle-competition/images/kfp-pipeline.PNG?raw=true" alt="kubeflow pipeline" width="600" height="700"/>
 </p>


# Section 2: Kale Pipeline

To create pipeline using the Kale JupyterLab extension


1. Clone GitHub repo and navigate to this directory

2. Install the requirements.txt file

3. Launch the digit-recognizer-kale.ipynb Notebook

4. Enable the Kale extension in JupyterLab 

5. Download JPX dataset using Kaggle's API. To do this, do the following:
   
   * Login to Kaggle and click on your user profile picture.
   * Click on ‘Account’.
   * Under ‘Account’, navigate to the ‘API’ section.
   * Click ‘Create New API token’.
   * After creating a new API token, a kaggle.json file is automatically downloaded, 
      and the json file contains the ‘api-key’ and ‘username’ needed to download the dataset.
   * Upload the JSON file to the Jupyter notebook instance
   * Pass the JSON file directory into the following cell.
<p>
<img src="https://github.com/josepholaide/examples/blob/master/jpx-tokyo-stock-exchange-kaggle-competition/images/pass-kaggle-json-path.PNG?raw=true" alt="pass kaggle json path" width="850" height="250"/>
 </p>
 
5. The notebook's cells are automatically annotated with Kale tags

   With the use of Kale tags we define the following:

   * Pipeline parameters are assigned using the "pipeline parameters" tag
   * The necessary libraries that need to be used throughout the Pipeline are passed through the "imports" tag
   * Notebook cells are assigned to specific Pipeline components (download data, load data, etc.) using the "pipeline step" tag
   * Cell dependencies are defined between the different pipeline steps with the "depends on" flag
   * Pipeline metrics are assigned using the "pipeline metrics" tag

6. Compile and run Notebook using Kale

### View Pipeline

<p>
<img src="https://github.com/josepholaide/examples/blob/master/jpx-tokyo-stock-exchange-kaggle-competition/images/kale-pipeline.PNG?raw=true" alt="kubeflow pipeline" width="600" height="700"/>
 </p>

