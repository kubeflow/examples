
# Notebook-based examples

This directory contains several notebook-based examples of how to deploy a [Kubeflow Pipeline](https://www.kubeflow.org/docs/pipelines/) from outside the Kubeflow cluster.

- [kfp_remote_deploy-IAP.ipynb](./kfp_remote_deploy-IAP.ipynb) shows how to do this with an IAP-enabled Kubeflow installation (on GKE).
- [gcf_kfp_trigger.ipynb](./gcf_kfp_trigger.ipynb) gives an example of how you can use
[GCF (Cloud Functions)](https://cloud.google.com/functions/) to support event-triggering of a Pipeline deployment to an IAP-enabled cluster (on GKE).
- [kfp_remote_deploy-port-forward.ipynb](./kfp_remote_deploy-port-forward.ipynb) walks through how to deploy via a port-forwarding connection to a cluster.
