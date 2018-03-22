# Training the model using TFJob

Kubeflow offers a TensorFlow job controller for kubernetes. This allows you to run your distributed Tensorflow training
job on a kubernetes cluster. For this training job, we will read our training data from GCS and write our output model
back to GCS.

## Create the image for training

The [tf-job](tf-job) directory contains the necessary files to create a image for training. The [train.py](tf-job/train.py) file contains the training code. Here is how you can create an image and push it to gcr.

```commandline
cd tf-job/
docker build . -t gcr.io/agwl-kubeflow/tf-job-issue-summarization:latest
gcloud docker -- push gcr.io/agwl-kubeflow/tf-job-issue-summarization:latest
```

## Service account

Create a [service account](https://console.cloud.google.com/iam-admin/serviceaccounts/) which will be used to read and write data from the GCS Bucket. Download it's key as a json file and save it to `key.json`.

Edit the GCS Bucket Permissions for the bucket which will contain the training data and give the service account `Storage Object Admin` or higher permissions.

Create a kubernetes secret with the file:

```
kubectl --namespace=${NAMESPACE} create secret generic gcp-credentials --from-file=key.json
```

## Run the TFJob using your image

[tf-job.yaml](tf-job/tf-job.yaml) contains the manifest to submit a training job. Edit the `args` field to set your GCS Bucket names and paths. Edit other fields to suit your training requirements. Then submit the job using:

```commandline
cd tf-job/
kubectl apply -f tf-job.yaml
```

In a while you should see a new pod with the label `name=tf-job-operator`
```
kubectl get pods -n=${NAMESPACE} -lname=tf-job-operator
```

You can view the logs using

```commandline
kubectl logs -f $(kubectl get pods -n=${NAMESPACE} -lname=tf-job-operator -o=jsonpath='{.items[0].metadata.name}')
```
