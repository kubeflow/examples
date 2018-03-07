# Serving the model

We are going to use a simple tornado server to serve the model. The [server.py](notebooks/server.py) contains the server code.

Start the server using `python server.py --port=8888`.

> The model is written in Keras and when exported as a TensorFlow model seems to be incompatible with TensorFlow Serving. So we're using our own webserver to serve this model. More details [here](https://github.com/kubeflow/examples/issues/11#issuecomment-371005885).

## Sample request

```
curl -X POST -H 'Content-Type: application/json' -d '{"instances": ["issue overview add a new property to disable detection of image stream files those ended with -is.yml from target directory. expected behaviour by default cube should not process image stream files if user does not set it. current behaviour cube always try to execute -is.yml files which can cause some problems in most of cases, for example if you are using kuberentes instead of openshift or if you use together fabric8 maven plugin with cube"]}' http://localhost:8888/predict
```

## Sample response

```
{"predictions": ["add a new property to disable detection"]}
```

Next: [Teardown](teardown.md)
