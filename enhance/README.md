# [WIP] Image enhancement

This is a work in progress.

Here we demonstrate the use of Kubeflow to perform distributed training and hyperparameter tuning of a TensorFlow model for enhancing brain microscopy images obtained from the [Allen Brain Institute](https://www.alleninstitute.org/) Mouse brain atlas. First we explore image de-noising using a simple Autoencoder model to learn an identity mapping between sub-images. Next we explore the process and usefulness of learning a model to perform image resolution up-sampling (or "super-resolution").

### Motivation

Removing blur, smudges, dust, or other artifacts from images is a need that spans not only all of experimental and clinical histology but all of biomedical imaging. Here we explore a general solution, inspired by [1], for image enhancement first in the form of same-resolution image cleanup and second in the form of image resolution up-sampling.

### Use case

The end use-case we envision with this example is batch processing of high-resolution images first as low-resolution sub-images stitched together into a final "enhanced" high-resolution image. Thus the deployment model for the product of the training phase is a batch data processing job. A user will make use of the resulting tooling simply by calling `batch-image-enhancer` pointing to a path containing images to process and indicating a directory where output should be stored.

```bash
image-enhancer --input /mnt/nfs-1/unprocessed --output /mnt/nfs-1/processed
```

### Usage

For documentation on each of the usage stages please refer to the corresponding documentation notebook:

- [Download](docs/download.ipynb)
- [[WIP]Datagen](docs/datagen.ipynb)
- [[WIP]Single training experiment](docs/t2t-experiment.ipynb)
- [[WIP]Running a hyperparameter study](docs/study.ipynb)
- [[WIP]Inference](docs/decode.ipynb)

### References

1. Romano, Yaniv, John Isidoro, and Peyman Milanfar. "RAISR: rapid and accurate image super resolution." IEEE Transactions on Computational Imaging 3.1 (2017): 110-125.