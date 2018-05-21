# Contributing Guide

You want to contribute to Kubeflow examples? That's awesome! Please refer to the short guide below. 

The [Kubeflow](https://github.com/kubeflow/kubeflow/blob/master/README.md) project is dedicated to
making machine learning on Kubernetes simple, portable, and scalable. We need your support in making
this repo the destination for top models and examples that highlight the power of Kubeflow.

## Example types

This repository is home to three types of examples, described in detail in the [README](./README.md):
1. [End-to-end](./README.md#end-to-end)
1. [Component-focused](./README.md#component-focused)
1. [Third-party hosted](./README.md#third-party-hosted)

## What we're looking for

Improvements to existing end-to-end and component-focused examples are always welcome. This could
mean smoothing out any rough edges, filling out support for additional runtime environments, fixing
bugs, and improving clarity in the instructions.

Additional component-focused examples for highly requested concepts are also encouraged. This could
include techniques such as:
* Recommendation
* Classification
* Vision

Extensions to our list of third-party hosted examples are also welcome. If it's useful to the community,
it belongs [here](./README.md#third-party-hosted)!

## How to contribute

Once you have identified an area for improvement, follow these steps:

1. Create a Github issue with the details and self-assign
1. Send a PR to this repo with the related fix or new content


## Requirements

Examples housed in this repo should have the following characteristics:

### Consistency

A good example fits in with existing examples. It follows the same conventions, has similar
structure, and does not stick out.

### Maintainability

A good example has longevity and is resistant to getting stale. It includes nightly tests and is
robust against releases.

### Approachability

A good example is not too complicated, including a small number of files and covering a single,
common use case. It makes use of well-known or straightforward datasets and performs well-understood
functions.

A good example is easily digestible by our user base. Each example does not need to cover all users,
but should accommodate at least one set of expected core competencies from the roles in this list:

* DevOps engineer
* ML engineer
* Data engineer
* Data scientist

### Extensibility

A good example can be extended to include additional components, runtime environments, and/or
techniques. It inspires extension by other members of the community.

### Friction-free

A good example is a self-contained landing spot for new users, which might mean that it includes
a link to end-to-end examples or cluster setup.

### Clear descriptions

A good example starts with an overview, usually containing the following pieces:
* Goals
* Non-goals
* Steps involved
* Intended audience
* Prerequisites
* Assumptions

It includes clear, well-organized step-by-step instructions that call out assumptions and provide
warnings about potential points of contention.

## Ideas for additional examples

This is a list of sources for potential new examples. Please feel free to self-assign by putting
your github ID in the appropriate column, creating a corresponding GitHub issue, and submitting
a PR.

Priority guidance: 

* **P0**: Very important, try to self-assign if there is a P0 available
* **P1**: Important, try to self-assign if there is no P0 available
* **P2**: Nice to have

# Proposed Examples

| Example | What does it accomplish? | Priority | Priority reasoning | ML framework | Owner (github_id) | Company | Github issue |
| -------- | :-----------------------: | :------: | :----------------: | :-----------: | :---------------: | :----: | :-----: |
| [GitHub issue summarization](./github_issue_summarization) | How to perform TensorFlow serving on Kubeflow e2e | **P0** | Desire to extend current support of Seldon serving | TensorFlow | | | |
| [Zillow housing prediction](https://www.kaggle.com/c/zillow-prize-1/kernels) | Zillow's home value prediction on Kaggle | **P0** | High prize Kaggle competition w/ opportunity to show XGBoost | XGBoost | [puneith](https://github.com/puneith) | Google | [issue #16](https://github.com/kubeflow/examples/issues/16) |
| [Mercari price suggestion challenge](https://www.kaggle.com/c/mercari-price-suggestion-challenge) | Automatically suggest product process to online sellers | **P0** | | | | | |
| [Airbnb new user bookings](https://www.kaggle.com/c/airbnb-recruiting-new-user-bookings) | Where will a new guest book their first travel experience | | | | | | |
| [TensorFlow object detection](https://github.com/tensorflow/models/tree/master/research/object_detection) | Object detection using TensorFlow API | | | | | | |
| [TFGAN](https://github.com/tensorflow/models/blob/master/research/gan/tutorial.ipynb) | Define, Train and Evaluate GAN | | GANs are of great interest currently | | | | |
| [Nested LSTM](https://github.com/hannw/nlstm) | TensorFlow implementation of nested LSTM cell | | LSTM are the canonical implementation of RNN to solve vanishing gradient problem and widely used for Time Series | | | | |
| [How to solve 90% of NLP problems: A step by step guide on Medium](https://blog.insightdatascience.com/how-to-solve-90-of-nlp-problems-a-step-by-step-guide-fda605278e4e) | Medium post on how to solve 90% of NLP problems from Emmanuel Ameisen | | Solves a really common problem in a generic way. Great example for people who want to do NLP and don't know how to do 80% of stuff like tokenzation, basic transforms, stop word removal etc and are boilerplate across every NLP task | | | | |
| [Tour of top-10 algorithms for ML newbies](https://towardsdatascience.com/a-tour-of-the-top-10-algorithms-for-machine-learning-newbies-dde4edffae11) | Top 10 algorithms for ML newbies | | Medium post with 8K claps and a guide for ML newbies to get started with ML | | | | | |
