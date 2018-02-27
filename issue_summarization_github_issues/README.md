# [WIP] End-to-End kubeflow tutorial using a Sequence-to-Sequence model

This example demonstrates how you can use `kubeflow` end-to-end to train and
serve a Sequence-to-Sequence model on an existing kubernetes cluster. This
tutorial is based upon @hamelsmu's article ["How To Create Data Products That
Are Magical Using Sequence-to-Sequence
Models"](https://medium.com/@hamelhusain/how-to-create-data-products-that-are-magical-using-sequence-to-sequence-models-703f86a231f8).

## Goals

There are two primary goals for this tutorial:

*   End-to-End kubeflow example
*   End-to-End Sequence-to-Sequence model

By the end of this tutorial, you should learn how to:

*   Setup a Kubeflow cluster on an existing Kubernetes deployment
*   Spawn up a Jupyter Notebook on the cluster
*   Spawn up a shared-persistent storage across the cluster to store large
    datasets
*   Train a Sequence-to-Sequence model using TensorFlow on the cluster using
    GPUs
*   Serve the model using TensorFlow Serving

## Steps:

1.  [Setup a Kubeflow cluster](setup_a_kubeflow_cluster.md)
1.  [Teardown](teardown.md)
