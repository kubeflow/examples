# Serving the model

We are going to use [seldon-core](https://github.com/SeldonIO/seldon-core) to serve the model. [IssueSummatization.py](notebooks/IssueSummatization.py) contains the code for this model. We will wrap this class into a seldon-core microservice which we can then deploy as a REST or GRPC API server.

> The model is written in Keras and when exported as a TensorFlow model seems to be incompatible with TensorFlow Serving. So we're using seldon-core to serve this model since seldon-core allows you to serve any arbitrary model. More details [here](https://github.com/kubeflow/examples/issues/11#issuecomment-371005885).

# Prerequisites

Ensure that you have the following files from the [training](training_the_model.md) step in your `notebooks` directory:

* `seq2seq_model_tutorial.h5` - the keras model
* `body_pp.dpkl` - the serialized body preprocessor
* `title_pp.dpkl` - the serialized title preprocessor

# Wrap the model into a seldon-core microservice

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

## Sample request and response

Request

```
curl -X POST -d 'json={"data":{"ndarray":[["issue overview add a new property to disable detection of image stream files those ended with -is.yml from target directory. expected behaviour by default cube should not process image stream files if user does not set it. current behaviour cube always try to execute -is.yml files which can cause some problems in most of cases, for example if you are using kuberentes instead of openshift or if you use together fabric8 maven plugin with cube"]]}}' http://localhost:5000/predict
```

Response

```
{
  "data": {
    "names": [
      "t:0"
    ],
    "ndarray": [
      [
        "add a new property to disable detection"
      ]
    ]
  }
}
```

Next: [Teardown](teardown.md)
