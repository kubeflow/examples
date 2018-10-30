# Querying the model

In this section, you will setup a web interface that can interact with a trained model server.


The web UI uses a Flask server to host the HTML/CSS/JavaScript files for the web page.
The Python program, mnist_client.py, contains a function that interacts directly with the prediction GRPC API exposed by our model server.

The following steps describe how to deploy the docker image in your Kubeflow cluster., the `web-ui` directory also contains a Dockerfile to build the application into a container image.

## Prerequisites

Ensure that your model is live and listening for GRPC requests as described in
[serving](03_serving_the_model.md).

## Deploy the front-end docker image to your kubernetes cluster

If you followed the instructions to [Deploy Kubeflow](https://www.kubeflow.org/docs/started/getting-started-gke/) on Google Kubernetes Engine
The folder `ks_app` from where Kubeflow was deployed contains the ksonnet components. We can generate the ui component which contains the frontend image deployment.

```commandline
cd ks_app
ks generate deployed-service web-ui --name=web-ui --image=gcr.io/kubeflow-examples/pytorch-mnist-ui --containerPort=5000 --servicePort=80
```

To serve the frontend interface, apply the `web-ui` component of the ksonnet app:

```
ks apply ${KF_ENV} -c web-ui
```

## View results from the frontend

You can port-forward the web-ui container locally:

```commandline
kubectl port-forward $(kubectl get pods -n ${NAMESPACE} -l app=web-ui -o jsonpath='{.items[0].metadata.name}') -n ${NAMESPACE} 8080:5000
```

In a browser, navigate to `http://localhost:8080/?name=mnist-classifier&addr=ambassador&port=80`, 
where name `mnist-classifier` is the deployment name of our model server, `addr` and `port` point to the Ambassador endpoint, 
which will route the request to the Seldon model service.


*Next*: [Teardown](05_teardown.md)

*Back*: [Serving the Model](03_serving_the_model.md)
