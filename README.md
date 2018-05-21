# kubeflow-examples

A repository to share extended Kubeflow examples and tutorials to demonstrate machine learning
concepts, data science workflows, and Kubeflow deployments. They illustrate the happy path,
acting as a starting point for new users and a reference guide for experienced users.

This repository is home to three types of examples:
1. [End-to-end](#end-to-end)
1. [Component-focused](#component-focused)
1. [Third-party hosted](#third-party-hosted)

## End-to-end

End-to-end examples are complete, soup to nuts walkthroughs that provide a starting point and
architectural guidelines. They are extensible over time and updated as new features appear in
Kubeflow and new tools/frameworks are supported. They can be large and are designed to be
choose-your-own-adventure style.

End-to-end examples each cover these concepts at a minimum:
1. Installing Kubeflow itself and any prerequisites
1. Training a model
1. Serving the trained model
1. Accessing and displaying predictions


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

## Component-focused

Component-focused examples assume an existing Kubeflow installation and are shorter in length.
They focus on a single concept such as a technique, component, or feature. They are designed
to be combined with other examples in any number of configurations.

## Third-party hosted

This is a list of examples maintained by third parties that demonstrate Kubeflow usage. This
category includes examples that highlight integration with other systems (as opposed to support
for them), such as case studies.

Other examples that belong in this list are media formats that are not
appropriate for inclusion in the repo directly, such as videos, blog posts, tweets, screenshots,
etc. This also includes cases where it does not make sense to conform pre-existing code to be
consistent with this repo.

Suggestions are always welcome for migration from third-party to directly hosted in this repo, 
given increased usefulness and/or alignment with release content.

| Source | Example | Description | 
| ------ | ------- | ----------- |
| | | | |


