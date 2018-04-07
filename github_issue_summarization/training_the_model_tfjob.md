# Training the model using TFJob

Kubeflow offers a TensorFlow job controller for kubernetes. This allows you to run your distributed Tensorflow training
job on a kubernetes cluster. For this training job, we will read our training data from GCS and write our output model
back to GCS.

## Create the image for training

The [notebooks](notebooks) directory contains the necessary files to create a image for training. The [train.py](notebooks/train.py) file contains the training code. Here is how you can create an image and push it to gcr.

```commandline
cd notebooks/
docker build . -t gcr.io/agwl-kubeflow/tf-job-issue-summarization:latest
gcloud docker -- push gcr.io/agwl-kubeflow/tf-job-issue-summarization:latest
```

## GCS Service account

* Create a service account which will be used to read and write data from the GCS Bucket.

* Give the storage account `roles/storage.admin` role so that it can access GCS Buckets.

* Download its key as a json file and create a secret named `gcp-credentials` with the key `key.json`

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

kubectl --namespace=${NAMESPACE} create secret generic gcp-credentials --from-file=key.json="${KEY_FILE}"
```


## Run the TFJob using your image

[notebooks](notebooks) contains a ksonnet app([ks-app](notebooks/ks-app)) to deploy the TFJob.

Create an environment to deploy the ksonnet app

```commandline
cd notebooks/ks-app
ks env add tfjob --namespace ${NAMESPACE}
```

Set the appropriate params for the tfjob component

```commandline
ks param set tfjob namespace ${NAMESPACE} --env=tfjob

# The image pushed in the previous step
ks param set tfjob image "gcr.io/agwl-kubeflow/tf-job-issue-summarization:latest" --env=tfjob

# Sample Size for training
ks param set tfjob sample_size 100000 --env=tfjob

# Set the input and output GCS Bucket locations
ks param set tfjob input_data_gcs_bucket "kubeflow-examples" --env=tfjob
ks param set tfjob input_data_gcs_path "github-issue-summarization-data/github-issues.zip" --env=tfjob
ks param set tfjob output_model_gcs_bucket "kubeflow-examples" --env=tfjob
ks param set tfjob output_model_gcs_path "github-issue-summarization-data/output_model.h5" --env=tfjob
```

Deploy the app:

```commandline
ks apply tfjob -c tfjob
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
