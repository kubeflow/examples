# Querying the model

In this section, you will setup a barebones web server that displays the
prediction provided by the previously deployed model.

The following steps describe how to build a docker image and deploy it locally,
where it accepts as input any arbitrary text and displays a
machine-generated summary.


## Prerequisites

Ensure that your model is live and listening for HTTP requests as described in
[serving](serving_the_model.md).


## Build the frontend image

To build the frontend image, issue the following commands:

```
cd docker
docker build -t gcr.io/gcr-repository-name/issue-summarization-ui .
```

## Store the frontend image

To store the image in a location accessible to GKE, push it to the container
registry of your choice. Here, it is pushed to Google Container Registry.

```
gcloud docker -- push gcr.io/gcr-repository-name/issue-summarization-ui:0.1
```

## Deploy the frontend image to your kubernetes cluster

To serve the frontend interface, run the image using the following command:

```
ks generate deployed-service issue-summarization-ui \
  --image gcr.io/gcr-repository-name/issue-summarization-ui:0.1 \
  --type ClusterIP
ks param set issue-summarization-ui namespace $NAMESPACE
ks apply cloud -c issue-summarization-ui
```

TODO: Figure out why deployed-service prototype does not pick up the
namespace parameter. The workaround is to generate the yaml for
issue-summarization-ui service and deployment objects, inserting
the namespace parameter, and applying manually to the cluster.


## View results from the frontend

To setup a proxy to the UI port running in k8s, issue the following command:

```
kubectl port-forward $(kubectl get pods -n ${NAMESPACE} -l app=issue-summarization-ui -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} 8081:80
```

In a browser, navigate to `http://localhost:8081`, where you will be greeted by "Issue
text" Enter text into the input box and click submit. You should see a
summary that was provided by your trained model.


Next: [Teardown](teardown.md)

