# Training MNIST using Kubeflow, S3, and Argo.

This example guides you through the process of taking an example model, modifying it to run better within Kubeflow, and serving the resulting trained model. We will be using Argo to manage the workflow, Tensorflow's S3 support for saving model training info, Tensorboard to visualize the training, and Kubeflow to deploy the Tensorflow operator and serve the model.

## Prerequisites

Before we get started there a few requirements.

### 1. Kubernetes Cluster Environment

For supported versions, please check Kubeflow document: https://v0-3.kubeflow.org/docs/started/getting-started/

### 2. ksonnect cli

```
curl -fksSL https://github.com/ksonnet/ksonnet/releases/download/v0.13.0/ks_0.13.0_linux_amd64.tar.gz \
    | tar --strip-components=1 -xvz -C /usr/local/bin/ ks_0.13.0_linux_amd64/ks
```

### 3. Kubeflow environment

```
git clone -b v0.3.2 https://github.com/kubeflow/kubeflow
./kubeflow/scripts/kfctl.sh init kf-app --platform none
cd kf-app
../kubeflow/scripts/kfctl.sh generate k8s
../kubeflow/scripts/kfctl.sh apply k8s
```

For detail info, check here: https://v0-3.kubeflow.org/docs/started/getting-started/

Note: The vizier-db in Kubeflow depends on a PV, you need to create it in order to make vizier-db work. But this does not affect this example.

### 4. argo cli

```
curl -sSL -o /usr/local/bin/argo https://github.com/argoproj/argo/releases/download/v2.2.1/argo-linux-amd64
chmod +x /usr/local/bin/argo
```


## Setup Minio[optional]

Minio provides an S3 compatible API, if you don't have S3 storage, then you can setup Minio.

If you use Minio, please also set `S3_USE_HTTPS=0`, `S3_VERIFY_SSL=0` and use `your-minio-ip:9000`  as `S3_ENDPOINT` and `http://your-minio-ip:9000`  as `AWS_ENDPOINT_URL` in following steps.

### 1. Deploy Minio

```
docker run -e MINIO_ACCESS_KEY=minio -e MINIO_SECRET_KEY=minio123 \
    --name=minio -d --net=host -v /var/lib/minio:/data minio/minio server /data
```

The Minio access key is `minio`, secret key is `minio123`, you can use them as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in following steps.

### 2. Create Minio bucket

```
mkdir /var/lib/minio/tfmnist
```

The Minio bucket name is `tfmnist`, you can use it as `BUCKET_NAME` in following steps.

If you want run more than one trainning and serving jobs, you can create another bucket and use it.


## Create tf service account

Due to lack of permissions in default serviceaccount, so we created a new one with the required permissions.

We will use `mnist` namespace for mnist model.

```
export NAMESPACE=mnist

kubectl create ns ${NAMESPACE}
kubectl -n ${NAMESPACE} apply -f tf-user.yaml
```

## Create secret for workflow

```
export S3_ENDPOINT=s3.us-west-2.amazonaws.com  #replace with your s3 endpoint
export AWS_ENDPOINT_URL=https://${S3_ENDPOINT} #use http instead of https for default minio installs
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
export AWS_REGION=us-west-2
export BUCKET_NAME=mybucket
export S3_USE_HTTPS=1 #set to 0 for default minio installs
export S3_VERIFY_SSL=1 #set to 0 for defaul minio installs

kubectl -n ${NAMESPACE} create secret generic aws-creds \
  --from-literal=awsAccessKeyID=${AWS_ACCESS_KEY_ID} --from-literal=awsSecretAccessKey=${AWS_SECRET_ACCESS_KEY}
```

## Submit training workflow

NOTE: By default this training workflow will enable model serving, you can disable model serving by passing `-p model-serving=false` to this workflow. And follow step 9 to enable model serving.

This training workflow is the bulk of the work, it contains:

1. Train the model
1. Export the model
1. Serve the model

Now let's look at how this is represented in our [example workflow](model-train.yaml)

The argo workflow can be daunting, but basically our steps above extrapolate as follows:

1. `get-workflow-info`: Generate and set variables for consumption in the rest of the pipeline.
1. `tensorboard`: Tensorboard is spawned, configured to watch the S3 URL for the training output.
1. `train-model`: A TFJob is spawned taking in variables such as number of workers, what path the datasets are at, which model container image, etc. The model is exported at the end.
1. `serve-model`: Optionally, the model is served.

With our workflow defined, we can now execute it.

```
export S3_DATA_URL=s3://${BUCKET_NAME}/data/mnist/
export S3_TRAIN_BASE_URL=s3://${BUCKET_NAME}/models
export JOB_NAME=myjob1
export TF_MODEL_IMAGE=siji/mnist-model:v1.11.0
export TF_WORKER=3
export MODEL_TRAIN_STEPS=200

argo submit model-train.yaml -n ${NAMESPACE} --serviceaccount tf-user \
    -p aws-endpoint-url=${AWS_ENDPOINT_URL} \
    -p s3-endpoint=${S3_ENDPOINT} \
    -p aws-region=${AWS_REGION} \
    -p tf-model-image=${TF_MODEL_IMAGE} \
    -p s3-data-url=${S3_DATA_URL} \
    -p s3-train-base-url=${S3_TRAIN_BASE_URL} \
    -p job-name=${JOB_NAME} \
    -p tf-worker=${TF_WORKER} \
    -p model-train-steps=${MODEL_TRAIN_STEPS} \
    -p s3-use-https=${S3_USE_HTTPS} \
    -p s3-verify-ssl=${S3_VERIFY_SSL} \
    -p namespace=${NAMESPACE}
```

Your training workflow should now be executing.

You can verify and keep track of your workflow using the argo commands:

```
$ argo -n ${NAMESPACE} list
NAME                STATUS    AGE   DURATION
tf-workflow-h7hwh   Running   1h    1h

$ argo -n ${NAMESPACE} get tf-workflow-h7hwh
```

After the STATUS to `Succeeded`, then you can use it.


## Submit serving workflow[optional]

**NOTE: Please only run this when you disable model serving in above step**

```
argo -n ${NAMESPACE} list # get the workflow name
WORKFLOW=<the workflow name>
argo submit model-deploy.yaml -n ${NAMESPACE} -p workflow=${WORKFLOW} --serviceaccount=tf-user
```

## Using Tensorflow serving

### 1. Install client requirements

```
pip install -r requirements.txt
```

### 2. Submit and query result

```
SERVICE_IP=$(kubectl -n ${NAMESPACE} get service -l app=mnist-${JOB_NAME} -o jsonpath='{.items[0].spec.clusterIP}')
TF_MODEL_SERVER_HOST=$SERVICE_IP TF_MNIST_IMAGE_PATH=data/7.png python mnist_client.py
```

This should result in output similar to this, depending on how well your model was trained:

```
outputs {
  key: "classes"
  value {
    dtype: DT_UINT8
    tensor_shape {
      dim {
        size: 1
      }
    }
    int_val: 7
  }
}
outputs {
  key: "predictions"
  value {
    dtype: DT_FLOAT
    tensor_shape {
      dim {
        size: 1
      }
      dim {
        size: 10
      }
    }
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 0.0
    float_val: 1.0
    float_val: 0.0
    float_val: 0.0
  }
}


............................
............................
............................
............................
............................
............................
............................
..............@@@@@@........
..........@@@@@@@@@@........
........@@@@@@@@@@@@........
........@@@@@@@@.@@@........
........@@@@....@@@@........
................@@@@........
...............@@@@.........
...............@@@@.........
...............@@@..........
..............@@@@..........
..............@@@...........
.............@@@@...........
.............@@@............
............@@@@............
............@@@.............
............@@@.............
...........@@@..............
..........@@@@..............
..........@@@@..............
..........@@................
............................
Your model says the above number is... 7!
```

You can also omit `TF_MNIST_IMAGE_PATH`, and the client will pick a random number from the mnist test data. Run it repeatedly and see how your model fares!


## Submitting new argo jobs

If you want to rerun your workflow from scratch, then you will need to provide a new `job-name` to the argo workflow. For example:

```
#We're re-using previous variables except JOB_NAME
export JOB_NAME=myawesomejob

argo submit model-train.yaml -n ${NAMESPACE} --serviceaccount tf-user \
    -p aws-endpoint-url=${AWS_ENDPOINT_URL} \
    -p s3-endpoint=${S3_ENDPOINT} \
    -p aws-region=${AWS_REGION} \
    -p tf-model-image=${TF_MODEL_IMAGE} \
    -p s3-data-url=${S3_DATA_URL} \
    -p s3-train-base-url=${S3_TRAIN_BASE_URL} \
    -p job-name=${JOB_NAME} \
    -p tf-worker=${TF_WORKER} \
    -p model-train-steps=${MODEL_TRAIN_STEPS} \
    -p s3-use-https=${S3_USE_HTTPS} \
    -p s3-verify-ssl=${S3_VERIFY_SSL} \
    -p namespace=${NAMESPACE}
```

## Conclusion and Next Steps

This is an example of what your machine learning pipeline can look like. Feel free to play with the tunables and see if you can increase your model's accuracy (increasing `model-train-steps` can go a long way).
