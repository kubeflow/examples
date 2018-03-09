# Kubeflow End to End - Part 2

(Previously)[README.md] we took an existing model and made a workflow to train and serve it with Kubeflow and Argo.

However one of the pain points was the copying of training information back and forth between containers.

TODO show the old diagram

As it turns out, Tensorflow has native S3 support! This means that anywhere a Tensorflow io operation is performed, an s3 url can be passed in (similarly to a GCS or HDFS URL).

This means our workflow can be simplified:

TODO simplified diagram

The s3-native workflow can seen here: (model-train-s3.yaml)[model-train-s3.yaml]

One notable change is that Tensorboard is now deployed before training to allow for monitoring. This couldn't be done in the previous part since the data was only collected at the end.
