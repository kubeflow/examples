// @apiVersion 0.1
// @name io.ksonnet.pkg.kubeflow-core
// @description Kubeflow core components
// @shortDescription Kubeflow core components. This currently includes JupyterHub and the TfJob controller.
// @param name string Name to give to each of the components
// @optionalParam namespace string null Namespace to use for the components. It is automatically inherited from the environment if not set.
// @optionalParam disks string null Comma separated list of Google persistent disks to attach to jupyter environments.
// @optionalParam cloud string null String identifying the cloud to customize the deployment for.
// @optionalParam AmbassadorServiceType string ClusterIP The service type for the API Gateway.
// @optionalParam AmbassadorImage string quay.io/datawire/ambassador:0.30.1 The image for the API Gateway.
// @optionalParam StatsdImage string quay.io/datawire/statsd:0.30.1 The image for the Stats and Monitoring.
// @optionalParam tfJobImage string gcr.io/kubeflow-images-public/tf_operator:v0.2.0 The image for the TfJob controller.
// @optionalParam tfDefaultImage string null The default image to use for TensorFlow.
// @optionalParam tfJobUiServiceType string ClusterIP The service type for the UI.
// @optionalParam jupyterHubServiceType string ClusterIP The service type for Jupyterhub.
// @optionalParam jupyterHubImage string gcr.io/kubeflow/jupyterhub-k8s:v20180531-3bb991b1 The image to use for JupyterHub.
// @optionalParam jupyterHubAuthenticator string null The authenticator to use
// @optionalParam jupyterNotebookPVCMount string /home/jovyan Mount path for PVC. Set empty to disable PVC
// @optionalParam jupyterNotebookRegistry string gcr.io The docker image registry for JupyterNotebook.
// @optionalParam jupyterNotebookRepoName string kubeflow-images-public The repoistory name for JupyterNotebook.
// @optionalParam reportUsage string false Whether or not to report Kubeflow usage to kubeflow.org.
// @optionalParam usageId string unknown_cluster Optional id to use when reporting usage to kubeflow.org
// @optionalParam tfJobVersion string v1alpha2 which version of the TFJob operator to use
// @optionalParam centralUiImage string gcr.io/kubeflow-images-public/centraldashboard:v0.2.1 Image to use for Central UI.

local k = import "k.libsonnet";
local all = import "kubeflow/core/all.libsonnet";

// updatedParams uses the environment namespace if
// the namespace parameter is not explicitly set
local updatedParams = params {
  namespace: if params.namespace == "null" then env.namespace else params.namespace,
};

std.prune(k.core.v1.list.new(all.parts(updatedParams).all))
