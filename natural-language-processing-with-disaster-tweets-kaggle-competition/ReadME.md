# Objective
<br>
The aim of this project is to correctly guide users through a tutorial of converting the https://www.kaggle.com/c/nlp-getting-started competition notebook into a Kubeflow pipeline.<br><br> 
There are 3 different ipynb files in this repo. The one ending with -orig is the original one from the competition, the one ending with -kpf uses vanilla kubeflow to create the pipeline and the one ending with -kale uses kale to build the kubeflow pipeline. <br>
<br>

If you do not already have Kubeflow installed,, you can obtain a free 14-day trial of Kubeflow as a Service here: https://www.arrikto.com/kubeflow-as-a-service/
<br><br>
We have two different ways of creating and running the pipeline. The first one is using vanilla KFP, and the second one is using Kale to simplify the process. The instructions to run both notebooks can be found below:

## Running the vanilla KFP version

The initial few steps to run either notebook are exactly the same. Then after the fourth step there is a big difference on how to convert the original competition notebook into a kubeflow pipeline, this can be clearly seen below:

1. Go to Kubeflow Dashboard and on the left panel click on Notebooks.

2. Click on the “+ New Notebook” button on the top right and create a notebook by giving it a name. Change the Workspace volume from from 5 GB to 50 GB, and change the requested memory to 6 GB.

3. After the set up is done, click on the Connect button next to the notebook you just created. It will take you to a JupyterLab.


4. In the JupyterLab launcher start a new terminal session to clone the github repo. In the terminal enter the following commands:

 ```$ git clone https://github.com/kubeflow/examples/natural-language-processing-with-disaster-tweets-kaggle-competition```

5. After succesfully cloning the repo, double click on the “natural-language-processing-with-disaster-tweets-kaggle-competition” folder. Then open the notebook named "natural-language-processing-with-disaster-tweets-kfp.ipynb" by double-clicking on this name in the left hand directory structure, and to run it click on the "restart the whole kernel and re-reun the whole notebook"(fast-forward logo-ed) button in the top menu of the notebook.

6. View run details immediately after submitting the pipeline.
<br><br>  
The differences in defining the KFP notebook from the original one require us to make note of the following changes: <br> <br>

 - Defining Functions : The function should be defined in such a way that every library which is being used inside it should be imported inside it. 

 - Passing data between components :  To pass big data files the best way is to use KPF components such as ```InputPath()``` and ```OutputPath()``` which store the location of the input and output files(generally we use this for big files such as CSV or big TEXT files). To download the data the best way is to pass an url and download it, use it in the function and store the output as a pickle file in the ```OutputPath()``` location and pass the ```OutputPath()``` as ```InputPath()``` to the next component and then extract the contents of the pickle file.

 - Converting the Functions into Components : We use: 

```
kfp.components.create_component_from_func()
```

This function takes mainly three arguments. The first one is the name of the function which is to be converted into a component, the second one is the list of packages to be installed as a list under the argument name as ```packages_to_install=[]```, and the final argument is the output_component_file which is defined by us as a .yaml file.


 - Defining Pipeline function : We now use ```@dsl.pipeline``` to define the pipeline. We add a name and description to the pipeline, and then define a function for this pipeline, which has arguments passed on, which are used as input to the components created earlier. We then pass the output of one component as input argument to the next component. 


 - Running the pipeline : To run the pipeline we use ```kfp.Client()```, and create an object of the class and then use ```create_run_from_pipeline_func``` function to run the pipeline by passing it the name of the pipeline and the arguments which are required as input.


![First Image](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(254).png)
![Second Iamge](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(255).png)
The final pipeline looks as shown below:<br>
![Pipeline Iamge](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(263).png)

## Running the Kale Version

### Understanding Kale Tags

With Kale you annotate cells (which are logical groupings of code) inside your Jupyter Notebook with tags. These tags tell Kuebflow how to interpret the code contained in the cell, what dependencies exist and what functionality is required to execute the cell.
<br><br>
### Step 1: Annotate the notebook with Kale tags

- In the left-hand sidebar of your Notebook, click on the Kale logo and enable it
- After enabling Kale, give the pipeline a name and description
- Next, click on the edit button on the right-hand side of each code block and select the cell-type for the cell, add a name to the cell and select the name of the pipeline step it depends on
- Select ```pipeline_step``` from cell-type for all pipeline steps and select ```skip``` as cell-type for cells which you want to skip in the pipeline
- **Note:** To make sure the pipeline works perfectly don’t forget to add the name of the component on which it depends. 

For example, in the screenshot below we annotate the code block with ```class_distribution``` and specify that it depends on the ```load_data``` step.
![Example Annotation Image](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(265).png)

<br><br>
Here’s the complete list of annotations for the Notebook along with the steps on which they are dependent on:<br><br>
![Table Annotation Image](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(272).png)

### Step 2: Running the Kubeflow pipeline
The steps to deploy the pipeline using Kale are as follows:

1. Go to Kubeflow Dashboard and on the left panel click on Notebooks.

2. Click on the “+ New Notebook” button on the top right and create a notebook by giving it a name. Change the Workspace volume from from 5 GB to 50 GB, and change the requested memory to 6 GB.

3. After the set up is done, click on the Connect button next to the notebook you just created. It will take you to a JupyterLab.


4. In the JupyterLab launcher start a new terminal session to clone the github repo. In the terminal enter the following commands:

```$ git clone https://github.com/kubeflow/examples/natural-language-processing-with-disaster-tweets-kaggle-competition```

5. After succesfully cloning the repo, double click on the "natural-language-processing-with-disaster-tweets-kaggle-competition" to go to the github repo. Then open the notebook named "natural-language-processing-with-disaster-tweets-kale.ipynb" by double-clicking on this name in the left hand directory structure. To run it first click on the first cell and run the code block containing the following code 
```pip install -r requirements.txt ```
then click on the "restart the whole kernel and re-rerun the whole notebook"(fast-forward logo-ed) button in the top menu of the notebook.

![Third Image](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(270).png)
![Fourth Image](https://github.com/AnkitRai-22/natural-language-processing-with-disaster-tweets-kaggle-competition/blob/main/images/Screenshot%20(271).png)
