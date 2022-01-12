KFP version: 1.7.0+
Kubernetes version: 1.17+

# Orchestrate Spark Jobs using Kubeflow pipelines

## Install kubeflow pipelines standalone or full kubeflow 

### for standalone kubeflow pipelines installation
https://www.kubeflow.org/docs/components/pipelines/installation/

### for full kubeflow installation
https://www.kubeflow.org/docs/started/installing-kubeflow/

## Install Spark Operator

https://github.com/GoogleCloudPlatform/spark-on-k8s-operator#installation

## Create Spark Service Account and add permissions

```
kubectl apply -f ./scripts/spark-rbac.yaml
```

## Run the notebok kubeflow-pipeline.ipynb 
 
## Access Kubflow/KFP UI

![image](/images/central-ui.png)

## OR

![image](/images/pipelines-ui.png)

## Upload pipeline

Upload the spark_job_pipeline.yaml file

![image](/images/upload-pipeline.png)

# Create Run

![image](/images/create-run.png)

# Start Pipeline add service account `spark-sa`

![image](/images/start_run.png)

# Wait till the execution is finished. check the `print-message` logs to view the result

![image](/images/final-output.png)
