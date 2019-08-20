
# Using the AutoML API from Kubeflow Pipelines

The [Kubeflow Pipeline](https://www.kubeflow.org/docs/pipelines/) in this directory shows a simple example of how you can make calls to the [AutoML Vision API](https://cloud.google.com/automl/) to build a pipeline that creates an AutoML *dataset* and then trains a model on that dataset.  It does this in two steps: one to create a *dataset* from a specified CSV file (as indicated in the AutoML Vision [documentation](https://cloud.google.com/vision/automl/docs/)), and a following step to train a model using the dataset.  The 'train' step blocks until the training completes, which — for this example — will be a max time of one hour.

This pipeline requires a GKE installation of Kubeflow, e.g. via the
['click to deploy' web app](https://deploy.kubeflow.cloud/#/deploy).

The two pipeline steps (components) use the same docker container.  You can see the `Dockerfile` for this container in [components/container/Dockerfile](./components/container/Dockerfile). The container's entry point is the [components/dataset_train/dataset_model.py](./components/dataset_train/dataset_model.py) file.  Take a look at this file to see how the AutoML API is being used.
(Currently the example trains for a budget of 1 hour, but it would easy to modify the pipeline to
pass a `train_budget` parameter as well.)


Once Kubeflow is installed on your GKE cluster, to run this pipeline, you'll need to vist the [IAM panel in the GCP Cloud Console](https://pantheon.corp.google.com/iam-admin/iam), find the Kubeflow-created service account
`<deployment>-user@<project>.iam.gserviceaccount.com`, and **add permissions to make that account an `AutoML Admin`**. This will give the Kubeflow Pipeline steps permission to call the AutoML APIs.

To run the example pipeline, upload the `automl_dataset_and_train.py.tar.gz` file to the Kubeflow Pipelines dashboard.
For the `csv-path` parameter, use the `gs://path/to/file` syntax. For the `dataset-name` and `model-name`, pick strings unique to the AutoML vision datasets and models for your project.

If you want to make changes to the code, re-run the [components/container/build.sh](./components/container/build.sh) script.  It will push a new container to your own project.  Edit the [automl_dataset_and_train.py](automl_dataset_and_train.py) pipeline script to point to your own container (instead of the one in `google-samples`), then [recompile the pipeline](https://www.kubeflow.org/docs/pipelines/sdk/build-component/#compile-the-pipeline) and upload the result to the Pipelines dashboard. (You'll need to have the [Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/install-sdk/) installed to do this.)
