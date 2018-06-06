# Serving the model

We are going to use [seldon-core](https://github.com/SeldonIO/seldon-core) to serve the model. [IssueSummarization.py](notebooks/IssueSummarization.py) contains the code for this model. We will wrap this class into a seldon-core microservice which we can then deploy as a REST or GRPC API server.

> The model is written in Keras and when exported as a TensorFlow model seems to be incompatible with TensorFlow Serving. So we're using seldon-core to serve this model since seldon-core allows you to serve any arbitrary model. More details [here](https://github.com/kubeflow/examples/issues/11#issuecomment-371005885).

#  Building a model server

You have two options for getting a model server

1. You can use the public model server image `gcr.io/kubeflow-examples/issue-summarization-model`

  * This server has a copy of the model and supporting assets baked into the container image
  * So you can just run this image to get a pre-trained model
  * Serving your own model using this server is discussed below

1. You can build your own model server as discussed below


## Wrap the model into a seldon-core microservice

cd into the notebooks directory and run the following docker command. This will create a build/ directory.

```
cd notebooks/
docker run -v $(pwd):/my_model seldonio/core-python-wrapper:0.7 /my_model IssueSummarization 0.1 gcr.io --base-image=python:3.6 --image-name=gcr-repository-name/issue-summarization
```

The build/ directory contains all the necessary files to build the seldon-core microservice image

```
cd build/
./build_image.sh
```

Now you should see an image named `gcr.io/gcr-repository-name/issue-summarization:0.1` in your docker images. To test the model, you can run it locally using

`docker run -p 5000:5000 gcr.io/gcr-repository-name/issue-summarization:0.1`

You can push the image by running `gcloud docker -- push gcr.io/gcr-repository-name/issue-summarization:0.1`

> You can find more details about wrapping a model with seldon-core [here](https://github.com/SeldonIO/seldon-core/blob/master/docs/wrappers/python.md)

### Storing a model in the Docker image

If you want to store a copy of the model in the Docker image make sure the following files are available in the directory in which you run
the commands in the previous steps. These files are produced by the [training](training_the_model.md) step in your `notebooks` directory:

* `seq2seq_model_tutorial.h5` - the keras model
* `body_pp.dpkl` - the serialized body preprocessor
* `title_pp.dpkl` - the serialized title preprocessor


# Deploying the model to your kubernetes cluster

Now that we have an image with our model server, we can deploy it to our kubernetes cluster. We need to first deploy seldon-core to our cluster.

## Deploy Seldon Core


Install the CRD and it's controller using the seldon prototype

```bash
cd ks-kubeflow
# Gives cluster-admin role to the default service account in the ${NAMESPACE}
kubectl create clusterrolebinding seldon-admin --clusterrole=cluster-admin --serviceaccount=${NAMESPACE}:default
# Install the kubeflow/seldon package
ks pkg install kubeflow/seldon
# Generate the seldon component and deploy it
ks generate seldon seldon --name=seldon --namespace=${NAMESPACE}
ks apply ${KF_ENV} -c seldon
```

Seldon Core should now be running on your cluster. You can verify it by running `kubectl get pods -n${NAMESPACE}`. You should see a pod named `seldon-cluster-manager-*`

## Deploying the actual model

Now that you have seldon core deployed, you can deploy the model using the `kubeflow/seldon-serve-simple` prototype.

```bash
ks generate seldon-serve-simple issue-summarization-model-serving \
  --name=issue-summarization \
  --image=gcr.io/gcr-repository-name/issue-summarization:0.1 \
  --namespace=${NAMESPACE} \
  --replicas=2
ks apply ${KF_ENV} -c issue-summarization-model-serving
```


# Sample request and response

Seldon Core uses ambassador to route it's requests. To send requests to the model, you can port-forward the ambassador container locally:

```
kubectl port-forward $(kubectl get pods -n ${NAMESPACE} -l service=ambassador -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} 8080:80
```


```
curl -X POST -H 'Content-Type: application/json' -d '{"data":{"ndarray":[["issue overview add a new property to disable detection of image stream files those ended with -is.yml from target directory. expected behaviour by default cube should not process image stream files if user does not set it. current behaviour cube always try to execute -is.yml files which can cause some problems in most of cases, for example if you are using kuberentes instead of openshift or if you use together fabric8 maven plugin with cube"]]}}' http://localhost:8080/seldon/issue-summarization/api/v0.1/predictions
```

Response

```
{
  "meta": {
    "puid": "2rqt023g11gt7vfr0jnfkf1hsa",
    "tags": {
    },
    "routing": {
    }
  },
  "data": {
    "names": ["t:0"],
    "ndarray": [["add a new property"]]
  }
}
```

*Next*: [Querying the model](04_querying_the_model.md)

*Back*: [Training the model](02_training_the_model.md)
