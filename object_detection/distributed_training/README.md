# Distributed TensorFlow Object Detection Training on K8s with [Kubeflow](https://github.com/kubeflow/kubeflow)
This example demonstrates how to use `kubeflow` to train an object detection model on an existing K8s cluster. This example is based on the TensorFlow [Pets tutorial](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_pets.md).

## Steps: 
1. [Setup a Kubeflow cluster](setup.md)
2. [Submit a distributed object detection training job](submit_job.md)
3. [Monitor your training job](monitor_job.md)
4. [Serve it through TensorFlow serving](export_tf_graph.md)
