# Querying the model

In this section, you will setup a barebones web server that displays the
prediction provided by the previously deployed model.

The following steps describe how to build a docker image and deploy it locally,
where it accepts as input any arbitrary text and displays a
machine-generated summary.


## Prerequisites

Ensure that your model is live and listening for HTTP requests as described in
[serving](serving_the_model.md). You should be able to query the trained model
by issuing POST requests to `http://localhost:8080`.


## Build the frontend image

To build the frontend image, issue the following commands:

```
cd docker
docker build -t gcr.io/gcr-repository-name/issue-summarization-fe .
```

## Store the frontend image

To store the image in a location accessible to GKE, push it to the container
registry of your choice. Here, it is pushed to Google Container Registry.

```
gcloud docker -- push gcr.io/gcr-repository-name/issue-summarization-fe:0.1
```

## Run the frontend image

To serve the frontend interface, run the image using the following command:

```
docker run --network host gcr.io/gcr-repository-name/issue-summarization-fe:0.1
```

TODO: Run with ksonnet, not locally

## View results from the frontend

In a browser, navigate to `http://localhost:8081`, where you will be greeted by "Issue
text" Enter text into the input box and click submit. You should see a
summary that was provided by your trained model.


Next: [Teardown](teardown.md)

