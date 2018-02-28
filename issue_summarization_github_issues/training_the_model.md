# Training the model

By this point, you should have a Jupyter Notebook running at `http://127.0.0.1:8000`.

For this tutorial, we are going to use a custom docker image which contains all the source code and python library dependencies required for this tutorial. Open the Jupyter Notebook and click on `Control Panel` button on the upper right hand side of the screen. Then click on `Stop My Server`. This terminates the current instance of Jupyter Notebook.

We are going to create a new instance from `JupyterHub`. Refresh the page and then click on `Start My Server`. Use the following docker image: `gcr.io/kubeflow-dev/issue-summarization-notebook-cpu:latest` in the Image field and click on `Spawn`.

This should create a new Jupyter Notebook which contains all the source code and python library dependencies required for this tutorial.

Open the Jupyter Notebook and navigate to the `notebooks` folder. Here you should see two files: `Tutorial.ipynb` and `seq2seq_utils.py`. Open `Tutorial.ipynb` - this contains a complete walk-through of how to go about downloading the training data, preprocessing it and training it.

Next: [Serving the model](serving_the_model.md)

## Note

The docker image `gcr.io/kubeflow-dev/issue-summarization-notebook-cpu:latest` is built using the Dockerfile and the source code in this directory.
