<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Training MNIST](#training-mnist)
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

# Training MNIST

This example guides you through the process of taking an example model, modifying it to run better within Kubeflow, and serving the resulting trained model.

## Prerequisites

Before we get started there a few requirements.

### Deploy Kubeflow

Follow the [Getting Started Guide](https://www.kubeflow.org/docs/started/getting-started/) to deploy Kubeflow

### Local Setup

You also need the following command line tools:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [ksonnet](https://ksonnet.io/#get-started)

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
DOCKER_URL=docker.io/reponame/mytfmodel # Put your docker registry here
docker build . --no-cache  -f Dockerfile.model -t ${DOCKER_URL}

docker push ${DOCKER_URL}
```

## Preparing your Kubernetes Cluster

With our data and workloads ready, now the cluster must be prepared. We will be deploying the TF Operator, and Argo to help manage our training job.

In the following instructions we will install our required components to a single namespace.  For these instructions we will assume the chosen namespace is `tfworkflow`:

### Training your model

#### Local storage

Let's start by runing the training job on Kubeflow and storing the model in a local storage. 

Fristly, refer to the [document](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) to create Persistent Volume(PV) and Persistent Volume Claim(PVC), the PVC name (${PVC_NAME}) will be used by pods of training and serving for local mode in steps below.

Creating an environment to store parameters particular for local mode.
```
KSENV=local
cd ks_app
ks env add ${KSENV}
```

Give the job a name to indicate it is running locally

```
ks param set --env=${KSENV} train name mnist-train-local
```

Point the job at your custom training image

```
ks param set --env=${KSENV} train image $DOCKER_URL
```

Mount the pvc to store the exported model, by default the pvc will be mounted to the `/mnt` of the training pod.

```
ks param set --env=${KSENV} train pvcName ${PVC_NAME}
```

Configure a filepath for the exported model and checkpoints.

```
ks param set --env=${KSENV} train modelDir /mnt
ks param set --env=${KSENV} train exportDir /mnt/export
```
You can now submit the job 

```
ks apply ${KSENV} -c train
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

Storing the model in GCS has the advantages

* The model is readily available after the job finishes
* We can run distributed training
   
  * Distributed training requires a storage system accessible to all the machines

Lets start by creating an environment to store parameters particular to writing the model to GCS
and running distributed.

```
KSENV=distributed
cd ks_app
ks env add ${KSENV}
```

Set an environment variable that points to your GCP project Id
```
PROJECT=<your project id>
```

Create a bucket on GCS to store our model. The name must be unique across all GCS buckets
```
BUCKET=$KSENV-$(date +%s)
gsutil mb gs://$BUCKET/
```

Give the job a different name (to distinguish it from your job which didn't use GCS)

```
ks param set --env=${KSENV} train name mnist-train-dist
```

Next we configure it to run distributed by setting the number of parameter servers and workers to use.

```
ks param set --env=${KSENV} train numPs 1
ks param set --env=${KSENV} train numWorkers 2
```
Now we need to configure parameters telling the code to save the model to GCS.

```
MODEL_PATH=my-model
ks param set --env=${KSENV} train modelDir gs://${BUCKET}/${MODEL_PATH}
ks param set --env=${KSENV} train exportDir gs://${BUCKET}/${MODEL_PATH}/export
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

  1. We stored the private key for this account in a K8s secret named `user-gcp-sa`

     * To see the secrets in your cluster
     
       ```
       kubectl get secrets -n kubeflow
       ```

  1. We granted this service account permission to read/write GCS buckets in this project

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

  1. Mount the secret into the pod 
       ```
       ks param set --env=${KSENV} train secret user-gcp-sa=/var/secrets
       ```

     * Note: ensure your envrionment is pointed at the same `kubeflow` namespace as the `user-gcp-sa` secret
     * Setting this ksonnet parameter causes a volumeMount and volume to be added to your TFJob
     * To see this you can run `ks show ${KSENV} -c train`

     * The output should now include a volumeMount and volume section

       ```
        apiVersion: kubeflow.org/v1beta1
        kind: TFJob
        metadata:
          ...
        spec:
          tfReplicaSpecs:
            Chief:
              ...
              template:
                ...
                spec:
                  containers:
                  - command:
                    ...
                    volumeMounts:
                    - mountPath: /var/secrets
                      name: user-gcp-sa
                      readOnly: true
                    ...
                  volumes:
                  - name: user-gcp-sa
                    secret:
                      secretName: user-gcp-sa
                  ...
       ```

  1. Next we need to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` so that our code knows
     where to look for the service account key.

     ```
     ks param set --env=${KSENV} train envVariables GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/user-gcp-sa.json     
     ```

     * If we look at the spec for our job we can see that the environment variable `GOOGLE_APPLICATION_CREDENTIALS` is set.

       ```
        ks show ${KSENV} -c train
       ```
       ```
        apiVersion: kubeflow.org/v1beta1
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
ks apply ${KSENV} -c train
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

To use S3 we need we need to configure TensorFlow to use S3 credentials and variables. These credentials will be provided as kubernetes secrets and the variables will be passed in as environment variables. Modify the below values to suit your environment.

Lets start by creating an environment to store parameters particular to writing the model to S3
and running distributed.

```
KSENV=distributed
cd ks_app
ks env add ${KSENV}
```

Give the job a different name (to distinguish it from your job which didn't use S3)

```
ks param set --env=${KSENV} train name mnist-train-dist
```

Next we configure it to run distributed by setting the number of parameter servers and workers to use.

```
ks param set --env=${KSENV} train numPs 1
ks param set --env=${KSENV} train numWorkers 2
```
Now we need to configure parameters telling the code to save the model to S3.

```
ks param set --env=${KSENV} train modelDir ${S3_MODEL_PATH_URI}
ks param set --env=${KSENV} train exportDir ${S3_MODEL_EXPORT_URI}
```

In order to write to S3 we need to supply the TensorFlow code with AWS credentials we also need to set
various environment variables configuring access to S3.

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

  1. Create a K8s secret containing your AWS credentials

     ```
     kubectl create secret generic aws-creds --from-literal=awsAccessKeyID=${AWS_ACCESS_KEY_ID} \
       --from-literal=awsSecretAccessKey=${AWS_SECRET_ACCESS_KEY}
     ```
  
  1. Pass secrets as environment variables into pod

     ```
     ks param set --env=${KSENV} train secretKeyRefs AWS_ACCESS_KEY_ID=aws-creds.awsAccessKeyID,AWS_SECRET_ACCESS_KEY=aws-creds.awsSecretAccessKey
     ```

     * Setting this ksonnet parameter causes a two new environment variables to be added to your TFJob
     * To see this you can run

       ```
       ks show ${KSENV} -c train
       ```

     * The output should now include two environment variables referencing K8s secret

       ```
       apiVersion: kubeflow.org/v1beta1
       kind: TFJob
       metadata:
         ...
       spec:
         tfReplicaSpecs:
           Chief:
             ...
             template:
               ...
               spec:
                 containers:
                 - command:
                   ...
                   env:
                   - name: AWS_ACCESS_KEY_ID
                     valueFrom:
                       secretKeyRef:
                         key: awsAccessKeyID
                         name: aws-creds
                   - name: AWS_SECRET_ACCESS_KEY
                     valueFrom:
                       secretKeyRef:
                         key: awsSecretAccessKey
                         name: aws-creds
                   ...
       ```
  
  1. Next we need to set a whole bunch of S3 related environment variables so that TensorFlow
     knows how to talk to S3

     ```
     AWSENV="S3_ENDPOINT=${S3_ENDPOINT}"
     AWSENV="${AWSENV},AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL}"     
     AWSENV="${AWSENV},AWS_REGION=${AWS_REGION}"
     AWSENV="${AWSENV},BUCKET_NAME=${BUCKET_NAME}"
     AWSENV="${AWSENV},S3_USE_HTTPS=${S3_USE_HTTPS}"
     AWSENV="${AWSENV},S3_VERIFY_SSL=${S3_VERIFY_SSL}"

     ks param set --env=${KSENV} train envVariables ${AWSENV}
     ```

     * If we look at the spec for our job we can see that the environment variables related 
     to S3 are set.

       ```
        ks show ${KSENV} -c train

        apiVersion: kubeflow.org/v1beta1
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
ks apply ${KSENV} -c train
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

Configure TensorBoard to point to your model location

```
ks param set tensorboard --env=${KSENV} logDir ${LOGDIR}
```

Assuming you followed the directions above if you used GCS you can use the following value

```
LOGDIR=gs://${BUCKET}/${MODEL_PATH}
```

You need to point TensorBoard to GCP credentials to access GCS bucket with model.

  1. Mount the secret into the pod

     ```
     ks param set --env=${KSENV} tensorboatd secret user-gcp-sa=/var/secrets
     ```

     * Setting this ksonnet parameter causes a volumeMount and volume to be added to TensorBoard
     deployment
     * To see this you can run

       ```
       ks show ${KSENV} -c tensorboard
       ```

     * The output should now include a volumeMount and volume section

  1. Next we need to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` so that our code knows
     where to look for the service account key.

     ```
     ks param set --env=${KSENV} tensorboard envVariables GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/user-gcp-sa.json     
     ```

     * If we look at the spec for TensorBoard deployment we can see that the environment variable `GOOGLE_APPLICATION_CREDENTIALS` is set.

       ```
       ks show ${KSENV} -c tensorboard
       ```
       ```
        ...
        env:
        ...
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/user-gcp-sa.json
       ```

#### Using S3

Configure TensorBoard to point to your model location

```
ks param set tensorboard --env=${KSENV} logDir ${LOGDIR}
```

Assuming you followed the directions above if you used S3 you can use the following value

```
LOGDIR=s3://${BUCKET}/${MODEL_PATH}
```

You need to point TensorBoard to AWS credentials to access S3 bucket with model.

  1. Pass secrets as environment variables into pod

     ```
     ks param set --env=${KSENV} tensorboard secretKeyRefs AWS_ACCESS_KEY_ID=aws-creds.awsAccessKeyID,AWS_SECRET_ACCESS_KEY=aws-creds.awsSecretAccessKey
     ```

     * Setting this ksonnet parameter causes a two new environment variables to be added to TensorBoard
     deployment
     * To see this you can run

       ```
       ks show ${KSENV} -c tensorboard
       ```

     * The output should now include two environment variables referencing K8s secret

       ```
        ...
        spec:
          containers:
          - command:
          ...
            env:
            ...
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  key: awsAccessKeyID
                  name: aws-creds
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  key: awsSecretAccessKey
                  name: aws-creds
                  ...
       ```

  1. Next we need to set a whole bunch of S3 related environment variables so that TensorBoard
     knows how to talk to S3

     ```
     AWSENV="S3_ENDPOINT=${S3_ENDPOINT}"
     AWSENV="${AWSENV},AWS_ENDPOINT_URL=${AWS_ENDPOINT_URL}"     
     AWSENV="${AWSENV},AWS_REGION=${AWS_REGION}"
     AWSENV="${AWSENV},BUCKET_NAME=${BUCKET_NAME}"
     AWSENV="${AWSENV},S3_USE_HTTPS=${S3_USE_HTTPS}"
     AWSENV="${AWSENV},S3_VERIFY_SSL=${S3_VERIFY_SSL}"

     ks param set --env=${KSENV} tensorboard envVariables ${AWSENV}
     ```

     * If we look at the spec for TensorBoard deployment we can see that the environment variables related to S3 are set.

       ```
       ks show ${KSENV} -c tensorboard
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
ks apply ${KSENV} -c tensorboard
```

To access TensorBoard using port-forwarding

```
kubectl -n jlewi port-forward service/tensorboard-tb 8090:80
```
TensorBoard can now be accessed at [http://127.0.0.1:8090](http://127.0.0.1:8090).


## Serving the model

The model code will export the model in saved model format which is suitable for serving with TensorFlow serving.

To serve the model follow the instructions below. The instructins vary slightly based on where you are storing your
model (e.g. GCS, S3, PVC). Depending on the storage system we provide different ksonnet components as a convenience
for setting relevant environment variables.


### GCS

Here we show to serve the model when it is stored on GCS. This assumes that when you trained the model you set `exportDir` to a GCS
URI; if not you can always copy it to GCS using `gsutil`.

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


Set your model path

```
ks param set --env=${KSENV} mnist-deploy-gcp modelBasePath ${EXPORT_DIR}
```

Deploy it

```
ks apply ${KSENV} -c mnist-deploy-gcp
```

You can check the deployment by running

```
kubectl describe deployments mnist-deploy-gcp
```

Finally, run a service to make the deployment accessible to other pods in the cluster

```
ks apply ${KSENV} -c mnist-service
```

The service should make the `mnist-deploy-gcp` deployment accessible over port 9000

```
kubectl describe service mnist-service
```

### S3

TODO: Add instructions

### Local storage

The section shows how to serve the local model that was stored in PVC while training.

Mount the PVC, by default the pvc will be mounted to the `/mnt` of the pod.

```
ks param set --env=${KSENV} mnist-deploy-local pvcName ${PVC_NAME}
```

Configure a filepath for the exported model.

```
ks param set --env=${KSENV} mnist-deploy-local modelBasePath /mnt/export
```

Deploy it.

```
ks apply ${KSENV} -c mnist-deploy-local
```

You can check the deployment by running
```
kubectl describe deployments mnist-deploy-local
```
Finally, run a service to make the deployment accessible to other pods in the cluster.
```
ks apply ${KSENV} -c mnist-service
```
The service should make the `mnist-deploy-local` deployment accessible over port 9000.
```
kubectl describe service mnist-service
```

## Web Front End

The example comes with a simple web front end that can be used with your model.

To deploy the web front end

```
ks apply ${KSENV} -c web-ui
```

### Connecting via port forwarding

To connect to the web app via port-forwarding

```
POD_NAME=$(kubectl get pods --selector=app=web-ui --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')

kubectl port-forward ${POD_NAME} 8080:5000  
```

You should now be able to open up the web app at [http://localhost:8080](http://localhost:8080).

### Using IAP on GCP

If you are using GCP and have set up IAP then you can access the web UI at

```
https://${DEPLOYMENT}.endpoints.${PROJECT}.cloud.goog/${NAMESPACE}/mnist/
```

## Conclusion and Next Steps

This is an example of what your machine learning can look like. Feel free to play with the tunables and see if you can increase your model's accuracy (increasing `model-train-steps` can go a long way).
