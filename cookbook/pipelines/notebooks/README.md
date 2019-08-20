
# Notebook-based examples

This directory contains several notebook-based examples of how to deploy a [Kubeflow Pipeline](https://www.kubeflow.org/docs/pipelines/) from outside the Kubeflow cluster.

- [kfp_remote_deploy.ipynb](./kfp_remote_deploy.ipynb) shows how to do this with an IAP-enabled Kubeflow installation (on GKE). 
- [kfp_remote_deploy-no-IAP.ipynb](./kfp_remote_deploy-no-IAP.ipynb) walks through how to connect via port-forwarding to the cluster
- [gcf_kfp_trigger.ipynb](./gcf_kfp_trigger.ipynb) gives an example of how you can use
[GCF (Cloud Functions)](https://cloud.google.com/functions/) to support event-triggering of a Pipeline deployment.
