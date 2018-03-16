# Kubeflow End to End - Part 2

(Previously)[README.md] we took an existing model and made a workflow to train and serve it with Kubeflow and Argo.

However one of the pain points was the copying of training information back and forth between containers. Additionally, much shimming was needed to get TF_CONFIG converted into command line arguments.

In this part we will optimize our workflow in a more kubeflow-native fashion by optmizing data handling, environment processing, and model monitoring.

## Data

This is the old workflow.

TODO show the old diagram

This seems fine, but as it turns out Tensorflow has native S3 support! This means that anywhere a Tensorflow io operation is performed, an s3 url can be passed in (similarly to a GCS or HDFS URL).

This means our workflow can be simplified:

TODO simplified diagram

The s3-native workflow can seen here: [model-train-s3.yaml](model-train-s3.yaml)

The major differences are the removal of any sidecar copying patterns. This ties into our monitoring story.

## Monitoring

In the previous part, Tensorboard was deployed after training was complete. This is good for a retrospective, however active monitoring would ideal. This may have been accomplished with a sidecar pattern, but it would make an already messy TFJob spec close to unreadable. Since all the training daemons are all streaming to S3 as they train, we can now monitor in real time.

TODO insert screenshot of tensorboard during training.

## Model Code improvments.

Shimming was another painpoint in the previous example. Most stock Tensorflow examples use command line arguments to pass information about the cluster spec, however the TFJob operator provides this cluster spec in TF_CONFIG.

Also we had to externalize the export functionality since it needed the complete training data from all workers to save the servable model. Now that everything is on S3, we can just finalize directly.

The differences are here:

TODO Insert Diff between last model and this model

And the total delta of our work is this:

TODO Insert diff between initial mnist example and the TFJob-native one.


#### Other TODOs


TODO follow up on https://github.com/tensorflow/tensorflow/issues/17203, or do example implementaton here to get rid of the shims.

TODO modify model to take TF_CONFIG

TODO modify model to finalize its own servable graph.

