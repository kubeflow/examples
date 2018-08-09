# Code Search on Kubeflow

This demo implements End-to-End Code Search on Kubeflow.

# Prerequisites

**NOTE**: If using the JupyterHub Spawner on a Kubeflow cluster, use the Docker image 
`gcr.io/kubeflow-images-public/kubeflow-codelab-notebook` which has baked all the pre-prequisites.

* `Kubeflow v0.2.2`
  This notebook assumes a Kubeflow cluster is already deployed. See
  [Getting Started with Kubeflow](https://www.kubeflow.org/docs/started/getting-started/).

* `Python 2.7` (bundled with `pip`) 
  For this demo, we will use Python 2.7. This restriction is due to [Apache Beam](https://beam.apache.org/),
  which does not support Python 3 yet (See [BEAM-1251](https://issues.apache.org/jira/browse/BEAM-1251)).

* `Google Cloud SDK`
  This example will use tools from the [Google Cloud SDK](https://cloud.google.com/sdk/). The SDK 
  must be authenticated and authorized. See
  [Authentication Overview](https://cloud.google.com/docs/authentication/).
  
* `Ksonnet 0.12`
  We use [Ksonnet](https://ksonnet.io/) to write Kubernetes jobs in a declarative manner to be run
  on top of Kubeflow.
  
# Usage

Follow along [this Jupyter Notebook](./code_search.ipynb) to execute various steps in the pipeline.

**NOTE**: This notebook can be run from the JupyterHub Spawner inside a Kubeflow cluster. 

# Acknowledgements

This project derives from [hamelsmu/code_search](https://github.com/hamelsmu/code_search).
