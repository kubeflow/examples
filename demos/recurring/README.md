# Kubeflow demo - Recurring runs with the KFP SDK

## 1. Setup your environment

This demo assumes that you have a functioning Kubeflow Pipelines deployment. If
not, follow the instructions
[here](https://www.kubeflow.org/docs/components/pipelines/installation/) and
[here](https://www.kubeflow.org/docs/components/pipelines/sdk/install-sdk/).

This demo has been verified to work with:
- KFP version `1.7.1`
- KFP SDK version `1.8.11`

Activate the conda environment you created following the above steps. 

Create a Jupyter kernel for your conda environment.

```bash
ipython kernel install --name "kfp" --user
```

## 2. Run the KFP SDK script

Step through the provided [notebook](recurring.ipynb) to create a recurring run
using the KFP SDK. Make sure to select the `kfp` kernel that you created
earlier. 

