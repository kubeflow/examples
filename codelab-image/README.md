# Kubeflow Codelab Notebook

This is a Jupyter notebook image intended for Kubeflow codelabs. It is based off the
public TensorFlow notebook, with the following additional components installed:
* ksonnet (version 0.12.0-rc1)
* annoy
* ktext
* nltk
* Pillow
* pydot

To build this image, run:
```
docker build --pull -t kubeflow-codelab-notebook:latest .
```

This image is published at `gcr.io/kubeflow-images-public/kubeflow-codelab-notebook`.
