# Compile, deploy and run kubeflow pipeline using Github Actions. 

This tutorial will go through how to use [Github Actions](https://github.com/features/actions) togheter with kubeflow for MLOps. The goal with this set up is to improve speed for test, deployment and also improve versioning and reproducibility. 

The tutorial will be based upon [this](https://github.com/marketplace/actions/kubeflow-compile-deploy-and-run) Github Action. 

## Initial setup
Before you start with this tutorial you need to have the following: 
- A GCP account
- [Kubeflow set up on GKE](https://www.kubeflow.org/docs/gke/deploy/deploy-cli/) using [IAP](https://www.kubeflow.org/docs/gke/deploy/oauth-setup/). 
- A service account with access to your Kubeflow deployment, see [here](https://github.com/kubeflow/examples/blob/cookbook/cookbook/pipelines/notebooks/kfp_remote_deploy-IAP.ipynb) section "Setup and configuration"  for example and needed accesses. 
- The code on GitHub

## Add secrets to Github repository

In order to the Github action to have access to your kubeflow deployment you need to add some [secrets to github](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets).

You have to add the following secrets: 
 - KUBEFLOW_URL - The url to your kubeflow deployment
 - ENCODED_GOOGLE_APPLICATION_CREDENTIALS - Service account with access to kubeflow and rights to deploy, see [here](http://amygdala.github.io/kubeflow/ml/2019/08/22/remote-deploy.html) for example, the credentials needs to be bas64 encode:

``` bash
cat path-to-key.json | base64
```
- CLIENT_ID - The IAP client id secret. 

[Here](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets) you can find how to add secrets. 

## Github action

For the github repository add a github action in the following folder from the root of the repository:  
```
.github/workflows/your_github_action_file.yml
```

This file should follow the convetion of [github workflows](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions)

The following is an example of a workflow file(can also be found in the file: "example_workflow.py"). 

```yaml
name: Compile, Deploy and Run on Kubeflow
on: [push]

# Set environmental variables

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: checkout files in repo
      uses: actions/checkout@master


    - name: Submit Kubeflow pipeline
      id: kubeflow
      uses: NikeNano/kubeflow-github-action@master
      with:
        KUBEFLOW_URL: ${{ secrets.KUBEFLOW_URL }}
        ENCODED_GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GKE_KEY }}
        GOOGLE_APPLICATION_CREDENTIALS: /tmp/gcloud-sa.json
        CLIENT_ID: ${{ secrets.CLIENT_ID }}
        PIPELINE_CODE_PATH: "example_pipeline.py"
        PIPELINE_FUNCTION_NAME: "flipcoin_pipeline"
        PIPELINE_PARAMETERS_PATH: "parameters.yaml"
        EXPERIMENT_NAME: "Default"
        RUN_PIPELINE: True
        VERSION_GITHUB_SHA: False

```
 
 Github workflows can be given names, and in the example the name is set to: "Compile, Deploy and Run on Kubeflow". This name will then be the name of the action when it runs on Github. 

 The ON arguments is replate to which actions on github should this workflow be triggered on. For more info see [here](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions#on)

"Runs on" defines which type of machine should the workflow be executed on, in this case it dont matter since we will use a action(NikeNano/kubeflow-github-action@master) which are containerize. 

A Github workflow is splitted to steps. In this example the first step will check out the code. This is needed in order to be abe to access the source code to the repo which the workflow is applied to. The firts action used is named "uses: actions/checkout@master", master here referst to the master branch of [the repository](https://github.com/actions/checkout) where this action is open sourced. 

The following step, named: "Submit Kubeflow pipeline" is the most interesting part for this tutorial. Within this step the connection to kubeflow is set up and depending on the user specified values. (see "with"). If you like to check the source code you can find it [here](https://github.com/NikeNano/kubeflow-github-action)(you can find more info on how to build actions [here](https://help.github.com/en/actions/building-actions)).

For the action you as a user need to specify the followng values in the "with" part: 
- KUBEFLOW_URL: The URL to your kubeflow deployment
- GKE_KEY: Service account with access to kubeflow and rights to deploy, see [here](http://amygdala.github.io/kubeflow/ml/2019/08/22/remote-deploy.html) for example, the credentials needs to be bas64 encode:

``` bash
cat path-to-key.json | base64
```
- GOOGLE_APPLICATION_CREDENTIALS: The path to where you like to store the secrets, which needs to be decoded from GKE_KEY
- CLIENT_ID: The IAP client secret
- PIPELINE_CODE_PATH: The full path to the python file containing the pipeline
- PIPELINE_FUNCTION_NAME: The name of the pipeline function the PIPELINE_CODE_PATH file
- PIPELINE_PARAMETERS_PATH: The pipeline parameters, path to yaml with the paramters, see file parameters.yaml for example. 
- EXPERIMENT_NAME: The name of the kubeflow experiment within which the pipeline should run
- RUN_PIPELINE: If you like to also run the pipeline set "True"
- VERSION_GITHUB_SHA: If the pipeline containers are versioned with the github hash. Set to False. Will be update with example later.  


## Usage

If you use the github workflow defined above, the workflow will be triggered on a push. You can see the workflow running on the tab "Actions" 

![Alt text](actions_ower_view.png?raw=true "Title")
_Figure 1_

![Alt text](check_action.png?raw=true "Title")
_Figure 1_

![Alt text](deep_dive.png?raw=true "Title")
_Figure 1_