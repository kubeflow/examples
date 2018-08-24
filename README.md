# kubeflow-examples

A repository to share extended Kubeflow examples and tutorials to demonstrate machine learning
concepts, data science workflows, and Kubeflow deployments. They illustrate the happy path,
acting as a starting point for new users and a reference guide for experienced users.

This repository is home to three types of examples:
1. [End-to-end](#end-to-end)
1. [Component-focused](#component-focused)
1. [Application-specific](#application-specific)

## End-to-end

### [GitHub issue summarization](./github_issue_summarization)
Author: [Hamel Husain](https://github.com/hamelsmu)

This example covers the following concepts:
1. Natural Language Processing (NLP) with Keras and Tensorflow
1. Connecting to Jupyterhub
1. Shared persistent storage
1. Training a Tensorflow model
  1. CPU
  1. GPU
1. Serving with Seldon Core
1. Flask front-end

### [MNIST](./mnist)

Author: [Elson Rodriguez](https://github.com/elsonrodriguez)

This example covers the following concepts:
1. Image recognition of handwritten digits
1. S3 storage
1. Training automation with Argo
1. Monitoring with Argo UI and Tensorboard
1. Serving with Tensorflow

### [Distributed Object Detection](./object_detection)

Author: [Daniel Castellanos](https://github.com/ldcastell)

This example covers the following concepts:
1. Gathering and preparing the data for model training using K8s jobs
1. Using Kubeflow tf-job and tf-operator to launch a distributed object training job
1. Serving the model through Kubeflow's tf-serving

## Component-focused

### [XGBoost - Ames housing price prediction](./xgboost_ames_housing)
Author: [Puneith Kaul](https://github.com/puneith)

This example covers the following concepts:
1. Training an XGBoost model
1. Shared persistent storage
1. GCS and GKE
1. Serving with Seldon Core


## Application-specific

1.

## Third-party hosted

| Source | Example | Description |
| ------ | ------- | ----------- |
| | | | |

## Get Involved

* [Slack Channel: #kubeflow-examples](https://join.slack.com/t/kubeflow/shared_invite/enQtMjgyMzMxNDgyMTQ5LWUwMTIxNmZlZTk2NGU0MmFiNDE4YWJiMzFiOGNkZGZjZmRlNTExNmUwMmQ2NzMwYzk5YzQxOWQyODBlZGY2OTg)
* [Twitter](http://twitter.com/kubeflow)
* [Mailing List](https://groups.google.com/forum/#!forum/kubeflow-discuss)

In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to making participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

The Kubeflow community is guided by our [Code of Conduct](https://github.com/kubeflow/community/blob/master/CODE_OF_CONDUCT.md), which we encourage everybody to read before participating.

