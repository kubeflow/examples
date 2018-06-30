# Training the model using TFJob

Kubeflow offers a TensorFlow job controller for kubernetes. This allows you to run your distributed Tensorflow training
job on a kubernetes cluster. For this training job, we will read our training data from GCS and write our output model
back to GCS.

## Create the image for training

The [notebooks](notebooks) directory contains the necessary files to create a image for training. The [train.py](notebooks/train.py) file contains the training code. Here is how you can create an image and push it to gcr.

```commandline
cd notebooks/
make PROJECT=${PROJECT} set-image
```
## Train Using PVC

If you don't have access to GCS or don't want to use GCS you
can use a persistent volume to store the data and model.

Create a pvc

```
ks apply --env=${KF_ENV} -c data-pvc
```
	
	* Your cluster must have a default storage class defined for
	  this to work.

Run the job to download the data to the PVC.

```
ks apply --env=${KF_ENV} -c data-downloader
```

Submit the training job

```
ks apply --env=${KF_ENV} -c tfjob-pvc
```

The resulting model will be stored on PVC so to access it you will
need to run a pod and attach the PVC. For serving you can just
attach it the pod serving the model.

## Training Using GCS

If you are running on GCS you can train using GCS to store the input
and the resulting model.

### GCS Service account

* Create a service account which will be used to read and write data from the GCS Bucket.

* Give the storage account `roles/storage.admin` role so that it can access GCS Buckets.

* Download its key as a json file and create a secret named `user-gcp-sa` with the key `user-gcp-sa.json`

```commandline
SERVICE_ACCOUNT=github-issue-summarization
PROJECT=kubeflow-example-project # The GCP Project name
gcloud iam service-accounts --project=${PROJECT} create ${SERVICE_ACCOUNT} \
  --display-name "GCP Service Account for use with kubeflow examples"

gcloud projects add-iam-policy-binding ${PROJECT} --member \
  serviceAccount:${SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com --role=roles/storage.admin

KEY_FILE=/home/agwl/secrets/${SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com.json
gcloud iam service-accounts keys create ${KEY_FILE} \
  --iam-account ${SERVICE_ACCOUNT}@${PROJECT}.iam.gserviceaccount.com

kubectl --namespace=${NAMESPACE} create secret generic user-gcp-sa --from-file=user-gcp-sa.json="${KEY_FILE}"
```


### Run the TFJob using your image

[ks-kubeflow](ks-kubeflow) contains a ksonnet app to deploy the TFJob.

Set the appropriate params for the tfjob component

```commandline
cd ks-kubeflow
ks param set tfjob namespace ${NAMESPACE} --env=${KF_ENV}

# The image pushed in the previous step
ks param set tfjob image "gcr.io/agwl-kubeflow/tf-job-issue-summarization:latest" --env=${KF_ENV}

# Sample Size for training
ks param set tfjob sample_size 100000 --env=${KF_ENV}

# Set the input and output GCS Bucket locations
ks param set tfjob input_data_gcs_bucket "kubeflow-examples" --env=${KF_ENV}
ks param set tfjob input_data_gcs_path "github-issue-summarization-data/github-issues.zip" --env=${KF_ENV}
ks param set tfjob output_model_gcs_bucket "kubeflow-examples" --env=${KF_ENV}
ks param set tfjob output_model_gcs_path "github-issue-summarization-data/output_model.h5" --env=${KF_ENV}
```

Deploy the app:

```commandline
ks apply ${KF_ENV} -c tfjob
```

In a while you should see a new pod with the label `tf_job_name=tf-job-issue-summarization`
```commandline
kubectl get pods -n=${NAMESPACE} -ltf_job_name=tf-job-issue-summarization
```

You can view the logs of the tf-job operator using

```commandline
kubectl logs -f $(kubectl get pods -n=${NAMESPACE} -lname=tf-job-operator -o=jsonpath='{.items[0].metadata.name}')
```

You can view the actual training logs using

```commandline
kubectl logs -f $(kubectl get pods -n=${NAMESPACE} -ltf_job_name=tf-job-issue-summarization -o=jsonpath='{.items[0].metadata.name}')
```

For information on:
- [Training the model](02_training_the_model.md)
- [Distributed training using tensor2tensor](02_tensor2tensor_training.md)

*Next*: [Serving the model](03_serving_the_model.md)

*Back*: [Setup a kubeflow cluster](01_setup_a_kubeflow_cluster.md)
