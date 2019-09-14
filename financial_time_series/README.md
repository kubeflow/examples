Using Kubeflow for Financial Time Series
====================

In this example, we will walk through the exploration, training and serving of a machine learning model by leveraging Kubeflow's main components. 
We will use the [Machine Learning with Financial Time Series Data](https://cloud.google.com/solutions/machine-learning-with-financial-time-series-data) use case.

### Pre-requisites
You can use a Google Cloud Shell to follow the steps outlined below.
In that case you can skip the requirements below as these depencies are pre-installed with the exception that you might still need to install ksonnet via these [instructions](https://www.kubeflow.org/docs/guides/components/ksonnet/).
You might also need to install ```uuid-runtime``` via ```sudo apt-get install uuid-runtime```.

Alternatively, you can work from your local environment.
In that case you will need a Linux or Mac environment with Python 3.6.x and install the following requirements
 * Install [Cloud SDK](https://cloud.google.com/sdk/)
 * Install [gcloud](https://cloud.google.com/sdk/gcloud/)
 * Install [ksonnet](https://ksonnet.io/#get-started) version 0.11.0 or later
 * Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

Independent of the machine that you are using, you will need access to a Google Cloud Project and its GKE resources.

### Deploying Kubeflow on GKE
The full deployment script for Kubeflow on GKE will create a cluster for you with machines that already have all the appropiate permissions.
Please follow the instructions on how to deploy Kubeflow to GKE on the [getting-started-GKE](https://v0-2.kubeflow.org/docs/started/getting-started-gke/) page from the `examples/financial_time_series` directory.

```
git clone https://github.com/kubeflow/examples.git
cd examples/financial_time_series/
<follow instructions for deploying GKE>
```
After the step `${KUBEFLOW_SRC}/scripts/kfctl.sh generate platform` make sure you add 'https://www.googleapis.com/auth/cloud-platform' to the `VM_OAUTH_SCOPES` in the file `{KFAPP}/gcp_config/cluster.ninja`. This will allow the machines to make use of the BigQuery API, which we need for our use case as the data is stored in BigQuery, and to store data on Google Cloud Storage. 
Also we will set `enableNodeAutoprovisioning` to false in this file as we will work with our dedicated gpu-pool. 
The [node autoprivioning](https://cloud.google.com/kubernetes-engine/docs/how-to/node-auto-provisioning) can be useful to autoscale the cluster with non-user defined node pools.

Next to this, we also need to update the `{KFAPP}/gcp_config/iam_bindings.yaml` by adding the roles 'roles/bigquery.admin' and 'roles/storage.admin' for the VM service account so that it is authorized to create a BigQuery job and write files to Google Cloud Storage.
Last but not least, we also need to update the `cluster-kubeflow.yaml` to enable GPUs on our cluster, set `gpu-pool-max-nodes` to 1 instead of 0.

Once the script is finished, you should a new folder in your directory`with the following subfolders.
```
$ financial_time_series
.
├── tensorflow_model
└── <kubeflow_src>
    ├── deployment
    ├── <kf_app>
    ├── kubeflow
    └── scripts
```
Next, we can easily verify the status of the pods by running ```kubectl get pods```.

### Explore the Kubeflow UI
After some time (about 10-15 minutes), an endpoint should now be available at `https://<kf_app>.endpoints.<project_id>.cloud.goog/`.
From this page you can navigate between the different Kubeflow components.

### Exploration via tf-hub
The TF-hub component of Kubeflow allows us to leverage [JupyterHub](https://github.com/jupyterhub/jupyterhub) to investigate the data and start building a feasible machine learning model for the specific problem.
From the Kubeflow starting page, you can click on the `Jupyterhub` tab.
After filling in a dummy username and password you are prompted to select parameters to spawn a JupyterHub.
In this case, we will just leave the default settings and hit spawn.

The following steps for running the Jupyter Notebook work better on a local machine kernel as the Google Cloud Shell is not meant to stand up a web socket service and is not configured for that.
Note that this is not a compulsory step in order to be able to follow the next sections, so if you are working on a Google Cloud Shell you can simply investigate the notebook via the link below.

You can simply upload the [notebook](https://github.com/kubeflow/examples/blob/master/financial_time_series/Financial%20Time%20Series%20with%20Finance%20Data.ipynb) and walk through it step by step to better understand the problem and suggested solution(s).
In this example, the goal is not focus on the notebook itself but rather on how this notebook is being translated in more scalable training jobs and later on serving.

### Training at scale with TF-jobs
The next step is to 're-factor' the notebook code into Python scripts which can then be containerized onto a Docker image.
In the folder ```tensorflow-model``` you can find these scripts together with a ```Dockerfile```.
Subsequently we will build a docker image on Google Cloud by running following command:

```
cd tensorflow-model/
export TRAIN_PATH=gcr.io/<project>/<image-name>/cpu:v1
gcloud builds submit --tag $TRAIN_PATH .
```

Now that we have an image ready on Google Cloud Container Registry, it's time we start launching a training job.

```
cd ../<kubeflow_src>/<kf_app>/ks_app
ks generate tf-job-simple train
```
This Ksonnet protoytype needs to be slightly modified to our needs, you can simply copy an updated version of this prototype by copying the updated version from the repository.
```
cp ../../../tensorflow_model/CPU/train.jsonnet ./components/train.jsonnet
```

Now we need to define the parameters which are currently set as placeholders in the training job prototype.
Note that this introduces a flexible and clean way of working, by changing the parameters you can easily launch another training job without maintaining multiple YAML files in your repository.

```
# create storage bucket that will be used to store models
BUCKET_NAME=<your-bucket-name>
gsutil mb gs://$BUCKET_NAME/
# set parameters
export TRAINING_NAME=trainingjob1
ks param set train name $TRAINING_NAME
ks param set train namespace "default"
ks param set train image $TRAIN_PATH
ks param set train workingDir "opt/workdir"
ks param set train args -- python,run_preprocess_and_train.py,--model=FlatModel,--epochs=30001,--bucket=$BUCKET_NAME,--version=1
```

You can verify the parameter settings in the params.libsonnet in the directory kubeflow_ks_app/components.
This file keeps track of all the parameters used to instantiate components from prototypes.
Next we can launch the tf-job to our Kubeflow cluster and follow the progress via the logs of the pod.

```
ks apply default -c train
POD_NAME=$(kubectl get pods --selector=tf_job_name=$TRAINING_NAME,tf-replica-type=worker \
      --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')
kubectl logs -f $POD_NAME
```

In the logs you can see that the trained model is being exported to google cloud storage. This saved model will be used later on for serving requests. With these parameters, the accuracy on the test set is approximating about 60%. 


### Deploy and serve with TF-serving
Once the model is trained, the next step will be to deploy it and serve requests.
Kubeflow comes with a TF-serving module which you can use to deploy your model with only a few commands.
```
ks generate tf-serving serve --name=tf-serving
ks param set serve modelPath gs://$BUCKET_NAME/model/
ks apply default -c serve
```
After running these commands, a deployment and service will be launched on Kubernetes that will enable you to easily send requests to get predictions from your module.
Let's check if the model is loaded successfully.

```
POD=`kubectl get pods --selector=app=tf-serving | awk '{print $1}' | tail -1`
kubectl logs -f $POD
```

We will do a local test via GRPC to illustrate how to get results from this serving component. Once the pod is up we can set up port-forwarding to our localhost.
```
kubectl port-forward $POD 9000:9000 2>&1 >/dev/null &
```

Now the only thing we need to do is send a request to ```localhost:9000``` with the expected input of the saved model and it will return a prediction.
The saved model expects a time series from closing stocks and spits out the prediction as a 0 (S&P closes positive) or 1 (S&P closes negative) together with the version of the saved model which was memorized upon saving the model.
Let's start with a script that populates a request with random numbers to test the service.
```
cd ../../../tensorflow_model
pip3 install numpy tensorflow-serving-api
python3 -m serving_requests.request_random
```

The output should return an integer, 0 or 1 as explained above, and a string that represents the version.
There is another script available that builds a more practical request, with time series data of closing stocks for a certain date.
In the following script, the same date is used as the one used at the end of the notebook ```Machine Learning with Financial Time Series Data.ipynb``` for comparison reasons.

```
pip3 install pandas
python3 -m serving_requests.request
```

The response should indicate that S&P index is expected to close positive (0) but from the actual data (which is prospected in the notebook mentioned above) we can see that it actually closed negative that day.
Let's get back to training and see if we can improve our accuracy.

### Running another tf-job and serving update
Most likely a single training job will never be sufficient. It is very common to create a continuous training pipeline to iterate training and verify the output.
Submitting another training job with Kubeflow is very easy.
By simply adjusting the parameters we can instantiate another component from the ```train.jsonnet```prototype.
This time, we will train a more complex neural network with several hidden layers.
```
cd ../<kubeflow_src>/<kf_app>/ks_app
export TRAINING_NAME=trainingjob2
ks param set train name $TRAINING_NAME
ks param set train args -- python,run_preprocess_and_train.py,--model=DeepModel,--epochs=30001,--bucket=$BUCKET_NAME,--version=2
ks apply default -c train
```

Verify the logs or use ```kubectl describe tfjobs trainingjob2```

```
POD_NAME=$(kubectl get pods --selector=tf_job_name=$TRAINING_NAME,tf-replica-type=worker \
      --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')
kubectl logs -f $POD_NAME
```

You should notice that the training now takes a few minutes instead of less than one minute, however the accuracy on the test set is now 72%.
Our training job uploads the trained model to the serving directory of our running tf-serving component.
The tf-serving component watches this serving directory and automatically loads the model of the folder with the highest version (as integer).
Since the newer version has a higher number than the previous one, our tf-serving should have switched to this new model.
Let's see if we get a response from the new version and if the new model gets it right this time.

```
cd ../../../tensorflow_model
python3 -m serving_requests.request
```

The response returns the updated version number '2' and  predicts the correct output 1, which means the S&P index closes negative, hurray!

### Running TF-job on a GPU

Can we also run the tf-job on a GPU?
Imagine the training job does not just take a few minutes but rather hours or days.
In this case we can reduce the training time by using a GPU. The GKE deployment script for Kubeflow automatically adds a GPU-pool that can scale as needed so you don’t need to pay for a GPU when you don’t need it. 
Note that the Kubeflow deployment also installs the necessary Nvidia drivers for you so there is no need for you to worry about extra GPU device plugins.

We will need another image that installs ```tensorflow-gpu``` and has the necessary drivers.

```
cp GPU/Dockerfile ./Dockerfile
export TRAIN_PATH_GPU=gcr.io/<project-name>/<image-name>/gpu:v1
gcloud builds submit --tag $TRAIN_PATH_GPU .
```

Also the train.jsonnet will need to be slightly adjusted to make it flexible to also run on GPUs.
You can simply copy the adjusted jsonnet by running following command.

```
cp GPU/train.jsonnet ../<kubeflow_src>/<kf_app>/ks_app/components/train.jsonnet
```



Subsequently, the parameters must be updated to fit with new prototype in ```train.jsonnet```.
```
cd ../<kubeflow_src>/<kf_app>/ks_app
export TRAINING_NAME=trainingjobgpu
ks param set train name $TRAINING_NAME
ks param set train gpuImage $TRAIN_PATH_GPU
ks param set train num_gpu 1
ks param set train args -- python,run_preprocess_and_train.py,--model=DeepModel,--epochs=30001,--bucket=$BUCKET_NAME,--version=3
```

Next we can deploy the tf-job to our GPU by simply running following command.

```
ks apply default -c train
```

First the pod will be unschedulable as there are no gpu-pool nodes available. This demand will be recognized by the kubernetes cluster and a node will be created on the gpu-pool automatically.
Once the pod is up, you can check the logs and verify that the training time is significantly reduced compared to the previous tf-job.
```
POD_NAME=$(kubectl get pods --selector=tf_job_name=$TRAINING_NAME,tf-replica-type=worker \
      --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')
kubectl logs -f $POD_NAME
```

### Kubeflow Pipelines
Up to now, we clustered the preprocessing and training in a single script to illustrate the TFJobs.
In practice, most often the preprocessing and training step will separated and they will need to run sequentially each time.
In this way, we decouple the preprocessing from the training and can iterate faster different ML flows.
Kubeflow pipelines offers an easy way of chaining these steps together and we will illustrate that here.
As you can see, the script `run_preprocess_and_train.py` was using the two scripts `run_preprocess.py` and `run_train.py` underlying.
The idea here is that these two steps will be containerized and chained together by Kubeflow pipelines.

KFP asks us to compile our pipeline Python3 file into a domain-specific-language. 
We do that with a tool called dsl-compile that comes with the Python3 SDK. So, first install that SDK:
```
pip3 install python-dateutil https://storage.googleapis.com/ml-pipeline/release/0.1.2/kfp.tar.gz --upgrade
```

Update the `ml_pipeline.py` with the cpu image path that you built in the previous steps and your bucket name.
Then, compile the DSL, using:
```
cd ../../../tensorflow_model
python3 ml_pipeline.py
```

Now a file `ml_pipeline.py.tar_gz` is generated that we can upload to the kubeflow pipelines UI.
We will navigate again back to the Kubeflow UI homepage on `https://<kf_app>.endpoints.<project_id>.cloud.goog/` and click on the Pipeline dashboard.


Once the browser is open, upload the tar.gz file. This simply makes the graph available. 
Next we can create a run and specify the params for the run. Make sure to specify version to 4 to check if this run creates a new saved model.
When the pipeline is running, you can inspect the logs:

![Pipeline UI](./docs/img/pipeline_ui.png "Kubeflow Pipeline UI")


### Clean up
To clean up, we will simply run the Kubeflow deletion bash script which takes care of deleting all components in a correct manner.

```
cd ../<kubeflow_src>/<kf_app>
${KUBEFLOW_REPO}/scripts/kfctl.sh delete all
```




