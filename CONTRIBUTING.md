# Contributing to Kubeflow Examples

You want to contribute to Kubeflow examples? That's awesome! Please refer to the short guide below. 

# Contributing Guide

The [Kubeflow](https://github.com/kubeflow/kubeflow/blob/master/README.md) project is dedicated to making machine learning on Kubernetes simple, portable and scalable. We need your support in making
this repo the destination for top models and examples, which show the power of Kubeflow. We have created an initial list of
proposed manifests. Please feel free to self-assign these examples, by following a simple 3 step process:

* Identify an **example** in table below and put your github id against it
* Create a Github issue with the details of the **example** and self-assign
* Send a PR to this repo with the actual work for the example

We have assigned priorities to the items below. See priority guidance: 

* **P0**: Very important, try to self-assign if there is a P0 available
* **P1**: Important, try to self-assign if there is no P0 available
* **P2**: Nice to have

# Proposed Examples

| Example | What does it accomplish? | Priority | Priority reasoning | ML framework | Owner (github_id) | Company | PR link |
| -------- | :-----------------------: | :------: | :----------------: | :-----------: | :---------------: | :----: | :-----: |
| TensorFlow serving end-to-end | How to perform TensorFlow serving on Kubeflow e2e | **P0** | TODO | TensorFlow | [nkash](https://github.com/nkashy1) | TODO | TODO |
| [Zillow housing prediction](https://www.kaggle.com/c/zillow-prize-1/kernels) | Zillow's home value prediction on Kaggle | **P0** | High prize Kaggle competition w/ opportunity to show XGBoost | XGBoost | [puneith](https://github.com/puneith) | Google | TODO |
| [Mercari price suggestion challenge](https://www.kaggle.com/c/mercari-price-suggestion-challenge) | Automatically suggest product proces to online sellers | **P0** | | | | | |
| [Airbnb new user bookings](https://www.kaggle.com/c/airbnb-recruiting-new-user-bookings) | Where will a new guest book their first travel experience | | | | | | |
| [TensorFlow object detection](https://github.com/tensorflow/models/tree/master/research/object_detection) | Object detection using TensorFlow API | | | | | | |
| [TFGAN](https://github.com/tensorflow/models/blob/master/research/gan/tutorial.ipynb) | Define, Train and Evaluate GAN | GANs are of great interest currently | | | | | |
| [Nested LSTM](https://github.com/hannw/nlstm) | TensorFlow implementation of nested LSTM cell | LSTM are the canonical implementation of RNN to solve vanishing gradient problem and widely used for Time Series | | | | | |
| [How to solve 90% of NLP problems: A step by step guide on Medium](https://blog.insightdatascience.com/how-to-solve-90-of-nlp-problems-a-step-by-step-guide-fda605278e4e) | Medium post on how to solve 90% of NLP problems from Emmanuel Ameisen | Solves a really common problem in a generic way. Great example for people who want to do NLP and don't know how to do 80% of stuff like tokenzation, basic transforms, stop word removal etc and are boilerplate across every NLP task | | | | | |
| [Tour of top-10 algorithms for ML newbies](https://towardsdatascience.com/a-tour-of-the-top-10-algorithms-for-machine-learning-newbies-dde4edffae11) | Top 10 algorithms for ML newbies | Medium post with 8K claps and a guide for ML newbies to get started with ML | | | | | |
