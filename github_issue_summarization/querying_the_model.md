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
docker build -t gcr.io/gcr-repository-name/issue-summarization-ui:0.1 .
```

## Store the frontend image

To store the image in a location accessible to GKE, push it to the container
registry of your choice. Here, it is pushed to Google Container Registry.

```
gcloud docker -- push gcr.io/gcr-repository-name/issue-summarization-ui:0.1
```

## Deploy the frontend image to your kubernetes cluster

The folder [ks-kubeflow](ks-kubeflow) contains a ksonnet app. The ui component in the ks-kubeflow app contains the frontend image deployment.

To avoid rate-limiting by the GitHub API, you will need an [authentication token](https://github.com/ksonnet/ksonnet/blob/master/docs/troubleshooting.md) stored in the form of an environment variable `${GITHUB_TOKEN}`. The token does not require any permissions and is only used to prevent anonymous API calls.

To use this token, set it as a parameter in the ui component:

```commandline
cd ks-kubeflow
ks param set ui github_token ${GITHUB_TOKEN} --env ${KF_ENV}
```

To serve the frontend interface, apply the ui component of the ksonnet app:

```
ks apply ${KF_ENV} -c ui
```

## View results from the frontend

We use ambassador to route requests to the frontend. You can port-forward the ambassador container locally:

```
kubectl port-forward $(kubectl get pods -n ${NAMESPACE} -l service=ambassador -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} 8080:80
```

In a browser, navigate to `http://localhost:8080/issue-summarization/`, where you will be greeted by "Issue
text" Enter text into the input box and click submit. You should see a
summary that was provided by your trained model.


Next: [Teardown](teardown.md)
