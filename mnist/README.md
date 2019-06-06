<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [MNIST on Kubeflow](#mnist-on-kubeflow)
  - [Prerequisites](#prerequisites)
    - [Deploy Kubeflow](#deploy-kubeflow)
    - [Local Setup](#local-setup)
  - [Modifying existing examples](#modifying-existing-examples)
    - [Prepare model](#prepare-model)
    - [Build and push model image.](#build-and-push-model-image)
  - [Preparing your Kubernetes Cluster](#preparing-your-kubernetes-cluster)
    - [Training your model](#training-your-model)
      - [Local storage](#local-storage)
      - [Using GCS](#using-gcs)
      - [Using S3](#using-s3)
  - [Monitoring](#monitoring)
    - [Tensorboard](#tensorboard)
      - [Using GCS](#using-gcs-1)
      - [Using S3](#using-s3-1)
      - [Deploying TensorBoard](#deploying-tensorboard)
  - [Serving the model](#serving-the-model)
    - [GCS](#gcs)
    - [S3](#s3)
    - [Local storage](#local-storage-1)
  - [Web Front End](#web-front-end)
    - [Connecting via port forwarding](#connecting-via-port-forwarding)
    - [Using IAP on GCP](#using-iap-on-gcp)
  - [Conclusion and Next Steps](#conclusion-and-next-steps)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# MNIST on Kubeflow

This example guides you through the process of taking an example model, modifying it to run better within Kubeflow, and serving the resulting trained model.

## Prerequisites

Before we get started there are a few requirements.

### Deploy Kubeflow

Follow the [Getting Started Guide](https://www.kubeflow.org/docs/started/getting-started/) to deploy Kubeflow.

### Local Setup

You also need the following command line tools:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [kustomize](https://kustomize.io/)

To run the client at the end of the example, you must have [requirements.txt](requirements.txt) intalled in your active python environment.

```
pip install -r requirements.txt
```

NOTE: These instructions rely on Github, and may cause issues if behind a firewall with many Github users. 

## Modifying existing examples

Many examples online use models that are unconfigurable, or don't work well in distributed mode. We will modify one of these [examples](https://github.com/tensorflow/tensorflow/blob/9a24e8acfcd8c9046e1abaac9dbf5e146186f4c2/tensorflow/examples/learn/mnist.py) to be better suited for distributed training and model serving.

### Prepare model

There is a delta between existing distributed mnist examples and what's needed to run well as a TFJob.

Basically, we must:

1. Add options in order to make the model configurable.
1. Use `tf.estimator.train_and_evaluate` to enable model exporting and serving.
1. Define serving signatures for model serving.

The resulting model is [model.py](model.py).

### Build and push model image.

With our code ready, we will now build/push the docker image.

```
DOCKER_URL=docker.io/reponame/mytfmodel:tag # Put your docker registry here
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_URL}

docker push ${DOCKER_URL}
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, and Argo to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `kubeflow`.

```
kubectl config set-context $(kubectl config current-context) --namespace=kubeflow
```

### Training your model

#### Local storage

Let's start by runing the training job on Kubeflow and storing the model in a local storage. 

Fristly, refer to the [document](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) to create Persistent Volume(PV) and Persistent Volume Claim(PVC), the PVC name (${PVC_NAME}) will be used by pods of training and serving for local mode in steps below.

Enter the `training/local` from the `mnist` application directory.
```
cd training/local
```

Give the job a name to indicate it is running locally

```
kustomize edit add configmap mnist-map-training --from-literal=name=mnist-train-local
```

Point the job at your custom training image

```
kustomize edit set image training-image=$DOCKER_URL
```

Optionally, configure it to run distributed by setting the number of parameter servers and workers to use. The `numPs` means the number of Ps and the `numWorkers` means the number of Worker.

```
../base/definition.sh --numPs 1 --numWorkers 2
```

Set the training parameters, such as training steps, batch size and learning rate.

```
kustomize edit add configmap mnist-map-training --from-literal=trainSteps=200
kustomize edit add configmap mnist-map-training --from-literal=batchSize=100
kustomize edit add configmap mnist-map-training --from-literal=learningRate=0.01
```

To store the the exported model and checkpoints model, configure PVC name and mount piont.

```
kustomize edit add configmap mnist-map-training --from-literal=pvcName=${PVC_NAME}
kustomize edit add configmap mnist-map-training --from-literal=pvcMountPath=/mnt
```

Now we need to configure parameters and telling the code to save the model to PVC.

```
kustomize edit add configmap mnist-map-training --from-literal=modelDir=/mnt
kustomize edit add configmap mnist-map-training --from-literal=exportDir=/mnt/export
```

You can now submit the job 

```
kustomize build . |kubectl apply -f -
```

And you can check the job

```
kubectl get tfjobs -o yaml mnist-train-local
```

And to check the logs 

```
kubectl logs mnist-train-local-chief-0
```


#### Using GCS

In this section we describe how to save the model to Google Cloud Storage (GCS).

Storing the model in GCS has the advantages:

* The model is readily available after the job finishes
* We can run distributed training
   
  * Distributed training requires a storage system accessible to all the machines

Enter the `training/GCS` from the `mnist` application directory.

```
cd training/GCS
```

Set an environment variable that points to your GCP project Id
```
PROJECT=<your project id>
```

Create a bucket on GCS to store our model. The name must be unique across all GCS buckets
```
BUCKET=distributed-$(date +%s)
gsutil mb gs://$BUCKET/
```

Give the job a different name (to distinguish it from your job which didn't use GCS)

```
kustomize edit add configmap mnist-map-training --from-literal=name=mnist-train-dist
```

Optionally, if you want to use your custom training image, configurate that as below.

```
kustomize edit set image training-image=$DOCKER_URL:$TAG
```

Next we configure it to run distributed by setting the number of parameter servers and workers to use. The `numPs` means the number of Ps and the `numWorkers` means the number of Worker.

```
../base/definition.sh --numPs 1 --numWorkers 2
```

Set the training parameters, such as training steps, batch size and learning rate.

```
kustomize edit add configmap mnist-map-training --from-literal=trainSteps=200
kustomize edit add configmap mnist-map-training --from-literal=batchSize=100
kustomize edit add configmap mnist-map-training --from-literal=learningRate=0.01
```

Now we need to configure parameters and telling the code to save the model to GCS.

```
MODEL_PATH=my-model
kustomize edit add configmap mnist-map-training --from-literal=modelDir=gs://${BUCKET}/${MODEL_PATH}
kustomize edit add configmap mnist-map-training --from-literal=exportDir=gs://${BUCKET}/${MODEL_PATH}/export
```

In order to write to GCS we need to supply the TFJob with GCP credentials. We do
this by telling our training code to use a [Google service account](https://cloud.google.com/docs/authentication/production#obtaining_and_providing_service_account_credentials_manually).

If you followed the [getting started guide for GKE](https://www.kubeflow.org/docs/started/getting-started-gke/) 
then a number of steps have already been performed for you

  1. We created a Google service account named `${DEPLOYMENT}-user`

     * You can run the following command to list all service accounts in your project

       ```
       gcloud --project=${PROJECT} iam service-accounts list
       ```

  2. We stored the private key for this account in a K8s secret named `user-gcp-sa`

     * To see the secrets in your cluster
     
       ```
       kubectl get secrets
       ```

  3. We granted this service account permission to read/write GCS buckets in this project

     * To see the IAM policy you can do

       ```
       gcloud projects get-iam-policy ${PROJECT} --format=yaml
       ```

     * The output should look like the following

       ```
        bindings:
        ...
        - members:
          - serviceAccount:${DEPLOYMENT}-user@${PROJEC}.iam.gserviceaccount.com
            ...
          role: roles/storage.admin
          ...
        etag: BwV_BqSmSCY=
        version: 1
        ```

To use this service account we perform the following steps

  1. Mount the secret `user-gcp-sa` into the pod and configure the mount path of the secret. 
       ```
       kustomize edit add configmap mnist-map-training --from-literal=secretName=user-gcp-sa
       kustomize edit add configmap mnist-map-training --from-literal=secretMountPath=/var/secrets
       ```

     * Note: ensure your envrionment is pointed at the same `kubeflow` namespace as the `user-gcp-sa` secret

  2. Next we need to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` so that our code knows where to look for the service account key.

     ```
     kustomize edit add configmap mnist-map-training --from-literal=GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/user-gcp-sa.json
     ```

     * If we look at the spec for our job we can see that the environment variable `GOOGLE_APPLICATION_CREDENTIALS` is set.

       ```
        kustomize build .
       ```
       ```
        apiVersion: kubeflow.org/v1beta2
        kind: TFJob
        metadata:
          ...
        spec:
          tfReplicaSpecs:
            Chief:
              replicas: 1
              template:
                spec:
                  containers:
                  - command:
                    ..
                    env:
                    ...
                    - name: GOOGLE_APPLICATION_CREDENTIALS
                      value: /var/secrets/user-gcp-sa.json
                    ...
                  ...
            ...
       ```


You can now submit the job

```
kustomize build . |kubectl apply -f -
```

And you can check the job status

```
kubectl get tfjobs -o yaml mnist-train-dist
```

And to check the logs 

```
kubectl logs -f mnist-train-dist-chief-0
```

#### Using S3

To use S3 we need to configure TensorFlow to use S3 credentials and variables. These credentials will be provided as kubernetes secrets and the variables will be passed in as environment variables. Modify the below values to suit your environment.

Enter the `training/S3` from the `mnist` application directory.

```
cd training/S3
```

Give the job a different name (to distinguish it from your job which didn't use S3)

```
kustomize edit add configmap mnist-map-training --from-literal=name=mnist-train-dist
```

Optionally, if you want to use your custom training image, configurate that as below.

```
kustomize edit set image training-image=$DOCKER_URL:$TAG
```

Next we configure it to run distributed by setting the number of parameter servers and workers to use. The `numPs` means the number of Ps and the `numWorkers` means the number of Worker.

```
../base/definition.sh --numPs 1 --numWorkers 2
```

Set the training parameters, such as training steps, batch size and learning rate.

```
kustomize edit add configmap mnist-map-training --from-literal=trainSteps=200
kustomize edit add configmap mnist-map-training --from-literal=batchSize=100
kustomize edit add configmap mnist-map-training --from-literal=learningRate=0.01
```

Now we need to configure parameters telling the code to save the model to S3, replace `${S3_MODEL_PATH_URI}` and `${S3_MODEL_EXPORT_URI}` below with real value.

```
kustomize edit add configmap mnist-map-training --from-literal=modelDir=${S3_MODEL_PATH_URI}
kustomize edit add configmap mnist-map-training --from-literal=exportDir=${S3_MODEL_EXPORT_URI}
```

In order to write to S3 we need to supply the TensorFlow code with AWS credentials we also need to set various environment variables configuring access to S3.

  1. Define a bunch of environment variables corresponding to your S3 settings; these will be used in subsequent steps

     ```
     export S3_ENDPOINT=s3.us-west-2.amazonaws.com  #replace with your s3 endpoint in a host:port format, e.g. minio:9000
     export AWS_ENDPOINT_URL=https://${S3_ENDPOINT} #use http instead of https for default minio installs
     export AWS_ACCESS_KEY_ID=xxxxx
     export AWS_SECRET_ACCESS_KEY=xxxxx
     export AWS_REGION=us-west-2
     export BUCKET_NAME=mybucket
     export S3_USE_HTTPS=1 #set to 0 for default minio installs
     export S3_VERIFY_SSL=1 #set to 0 for defaul minio installs 
     ```

  2. Create a K8s secret containing your AWS credentials

     ```
     kustomize edit add secret aws-creds --from-literal=awsAccessKeyID=${AWS_ACCESS_KEY_ID} \
       --from-literal=awsSecretAccessKey=${AWS_SECRET_ACCESS_KEY}
     ```

  3. Pass secrets as environment variables into pod

     ```
     kustomize edit add configmap mnist-map-training --from-literal=awsSecretName=aws-creds
     kustomize edit add configmap mnist-map-training --from-literal=awsAccessKeyIDName=awsAccessKeyID
     kustomize edit add configmap mnist-map-training --from-literal=awsSecretAccessKeyName=awsSecretAccessKey
     ```   

  4. Next we need to set a whole bunch of S3 related environment variables so that TensorFlow knows how to talk to S3

     ```
     kustomize edit add configmap mnist-map-training --from-literal=S3_ENDPOINT=${S3_ENDPOINT}
     kustomize edit add configmap mnist-map-training --from-literal=AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL}
     kustomize edit add configmap mnist-map-training --from-literal=AWS_REGION=${AWS_REGION}
     kustomize edit add configmap mnist-map-training --from-literal=BUCKET_NAME=${BUCKET_NAME}
     kustomize edit add configmap mnist-map-training --from-literal=S3_USE_HTTPS=${S3_USE_HTTPS}
     kustomize edit add configmap mnist-map-training --from-literal=S3_VERIFY_SSL=${S3_VERIFY_SSL}
     ```

     * If we look at the spec for our job we can see that the environment variables related to S3 are set.

       ```
        kustomize build .

        apiVersion: kubeflow.org/v1beta2
        kind: TFJob
        metadata:
          ...
        spec:
          tfReplicaSpecs:
            Chief:
              replicas: 1
              template:
                spec:
                  containers:
                  - command:
                    ..
                    env:
                    ...
                    - name: AWS_REGION
                      value: us-west-2
                    - name: BUCKET_NAME
                      value: somebucket
                    ...
                  ...
            ...
       ```


You can now submit the job

```
kustomize build . |kubectl apply -f -
```

And you can check the job

```
kubectl get tfjobs -o yaml mnist-train-dist
```

And to check the logs 

```
kubectl logs -f mnist-train-dist-chief-0
```

## Monitoring

There are various ways to monitor workflow/training job. In addition to using `kubectl` to query for the status of `pods`, some basic dashboards are also available.

### Tensorboard

#### Using GCS

Enter the `monitoring/GCS` from the `mnist` application directory.

```
cd monitoring/GCS
```

Configure TensorBoard to point to your model location

```
kustomize edit add configmap mnist-map-monitoring --from-literal=logDir=${LOGDIR}
```

Assuming you followed the directions above if you used GCS you can use the following value

```
LOGDIR=gs://${BUCKET}/${MODEL_PATH}
```

You need to point TensorBoard to GCP credentials to access GCS bucket with model.

  1. Mount the secret `user-gcp-sa` into the pod and configure the mount path of the secret. 
       ```
       kustomize edit add configmap mnist-map-monitoring --from-literal=secretName=user-gcp-sa
       kustomize edit add configmap mnist-map-monitoring --from-literal=secretMountPath=/var/secrets
       ```

     * Setting this parameter causes a volumeMount and volume to be added to TensorBoard deployment

  2. Next we need to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` so that our code knows
     where to look for the service account key.

     ```
     kustomize edit add configmap mnist-map-monitoring --from-literal=GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/user-gcp-sa.json     
     ```

     * If we look at the spec for TensorBoard deployment we can see that the environment variable `GOOGLE_APPLICATION_CREDENTIALS` is set.

       ```
       kustomize build .
       ```
       ```
        ...
        env:
        ...
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/user-gcp-sa.json
       ```

#### Using S3

Enter the `monitoring/S3` from the `mnist` application directory.

```
cd monitoring/S3
```

Configure TensorBoard to point to your model location

```
kustomize edit add configmap mnist-map-monitoring --from-literal=logDir=${LOGDIR}
```

Assuming you followed the directions above if you used S3 you can use the following value

```
LOGDIR=s3://${BUCKET}/${MODEL_PATH}
```

You need to point TensorBoard to AWS credentials to access S3 bucket with model.

  1. Pass secrets as environment variables into pod

     ```
     kustomize edit add configmap mnist-map-monitoring --from-literal=awsSecretName=aws-creds
     kustomize edit add configmap mnist-map-monitoring --from-literal=awsAccessKeyIDName=awsAccessKeyID
     kustomize edit add configmap mnist-map-monitoring --from-literal=awsSecretAccessKeyName=awsSecretAccessKey
     ```

  2. Next we need to set a whole bunch of S3 related environment variables so that TensorBoard knows how to talk to S3

     ```
     kustomize edit add configmap mnist-map-monitoring --from-literal=S3_ENDPOINT=${S3_ENDPOINT}
     kustomize edit add configmap mnist-map-monitoring --from-literal=AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL}
     kustomize edit add configmap mnist-map-monitoring --from-literal=AWS_REGION=${AWS_REGION}
     kustomize edit add configmap mnist-map-monitoring --from-literal=BUCKET_NAME=${BUCKET_NAME}
     kustomize edit add configmap mnist-map-monitoring --from-literal=S3_USE_HTTPS=${S3_USE_HTTPS}
     kustomize edit add configmap mnist-map-monitoring --from-literal=S3_VERIFY_SSL=${S3_VERIFY_SSL}
     ```

     * If we look at the spec for TensorBoard deployment we can see that the environment variables related to S3 are set.

       ```
       kustomize build .
       ```

       ```
        ...
        spec:
          containers:
          - command:
            ..
            env:
            ...
            - name: AWS_REGION
              value: us-west-2
            - name: BUCKET_NAME
              value: somebucket
            ...
       ```


#### Deploying TensorBoard

Now you can deploy TensorBoard

```
kustomize build . | kubectl apply -f -
```

To access TensorBoard using port-forwarding

```
kubectl port-forward service/tensorboard-tb 8090:80
```
TensorBoard can now be accessed at [http://127.0.0.1:8090](http://127.0.0.1:8090).

## Serving the model

The model code will export the model in saved model format which is suitable for serving with TensorFlow serving.

To serve the model follow the instructions below. The instructins vary slightly based on where you are storing your model (e.g. GCS, S3, PVC). Depending on the storage system we provide different kustomization as a convenience for setting relevant environment variables.


### GCS

Here we show to serve the model when it is stored on GCS. This assumes that when you trained the model you set `exportDir` to a GCS URI; if not you can always copy it to GCS using `gsutil`.

Check that a model was exported

```
EXPORT_DIR=gs://${BUCKET}/${MODEL_PATH}/export
gsutil ls -r ${EXPORT_DIR}
```

The output should look something like

```
${EXPORT_DIR}/1547100373/saved_model.pb
${EXPORT_DIR}/1547100373/variables/:
${EXPORT_DIR}/1547100373/variables/
${EXPORT_DIR}/1547100373/variables/variables.data-00000-of-00001
${EXPORT_DIR}/1547100373/variables/variables.index
```

The number `1547100373` is a version number auto-generated by TensorFlow; it will vary on each run but should be monotonically increasing if you save a model to the same location as a previous location.

Enter the `serving/GCS` from the `mnist` application directory.
```
cd serving/GCS
```

Set a different name for the tf-serving.

```
kustomize edit add configmap mnist-map-serving --from-literal=name=mnist-gcs-dist
```

Set your model path

```
kustomize edit add configmap mnist-map-serving --from-literal=modelBasePath=${EXPORT_DIR} 
```

Deploy it, and run a service to make the deployment accessible to other pods in the cluster

```
kustomize build . |kubectl apply -f -
```

You can check the deployment by running

```
kubectl describe deployments mnist-gcs-dist
```

The service should make the `mnist-gcs-dist` deployment accessible over port 9000

```
kubectl describe service mnist-gcs-dist
```

### S3

TODO: Add instructions

### Local storage

The section shows how to serve the local model that was stored in PVC while training.

Enter the `serving/local` from the `mnist` application directory.

```
cd serving/local
```

Set a different name for the tf-serving.

```
kustomize edit add configmap mnist-map-serving --from-literal=name=mnist-service-local
```

Mount the PVC, by default the pvc will be mounted to the `/mnt` of the pod.

```
kustomize edit add configmap mnist-map-serving --from-literal=pvcName=${PVC_NAME}
kustomize edit add configmap mnist-map-serving --from-literal=pvcMountPath=/mnt
```

Configure a filepath for the exported model.

```
kustomize edit add configmap mnist-map-serving --from-literal=modelBasePath=/mnt/export
```

Deploy it, and run a service to make the deployment accessible to other pods in the cluster.

```
kustomize build . |kubectl apply -f -
```

You can check the deployment by running
```
kubectl describe deployments mnist-deploy-local
```

The service should make the `mnist-deploy-local` deployment accessible over port 9000.
```
kubectl describe service mnist-service
```

## Web Front End

The example comes with a simple web front end that can be used with your model.

Enter the `front` from the `mnist` application directory.

```
cd front
```

To deploy the web front end

```
kustomize build . |kubectl apply -f -
```

### Connecting via port forwarding

To connect to the web app via port-forwarding

```
POD_NAME=$(kubectl get pods --selector=app=web-ui --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')

kubectl port-forward ${POD_NAME} 8080:5000  
```

You should now be able to open up the web app at Local Storage: [http://localhost:8080](http://localhost:8080) and GCS: [http://localhost:8080/?addr=mnist-gcs-dist](http://localhost:8080/?addr=mnist-gcs-dist)


### Using IAP on GCP

If you are using GCP and have set up IAP then you can access the web UI at

```
https://${DEPLOYMENT}.endpoints.${PROJECT}.cloud.goog/${NAMESPACE}/mnist/
```

## Conclusion and Next Steps

This is an example of what your machine learning can look like. Feel free to play with the tunables and see if you can increase your model's accuracy (increasing `model-train-steps` can go a long way).
