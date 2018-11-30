{
  global: {},
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "data-pvc": {
    },
    seldon: {
      apifeImage: "seldonio/apife:0.1.5",
      apifeServiceType: "NodePort",
      engineImage: "seldonio/engine:0.1.5",
      name: "seldon",
      namespace: "null",
      operatorImage: "seldonio/cluster-manager:0.1.5",
      operatorJavaOpts: "null",
      operatorSpringOpts: "null",
      withApife: "false",
      withRbac: "true",
    },
    "issue-summarization-model-serving": {
      endpoint: "REST",
      image: "gcr.io/kubeflow-examples/issue-summarization-model:v20180427-e2aa113",
      name: "issue-summarization",
      namespace: "null",
      replicas: 2,
    },
    tensorboard: {
      image: "tensorflow/tensorflow:1.7.0",
      // logDir needs to be overwritten based on where the data is
      // actually stored.
      logDir: "",
      name: "gh",
    },
    ui: {
      namespace: "null",
      githubToken: "",
      image: "gcr.io/kubeflow-examples/issue-summarization-ui:v20180629-v0.1-2-g98ed4b4-dirty-182929",
    },
    "tfjob-v1alpha2": {
      name: "tfjob-issue-summarization",
      image: "gcr.io/kubeflow-examples/tf-job-issue-summarization:v20180629-v0.1-2-g98ed4b4-dirty-182929",
      input_data_gcs_bucket: "kubeflow-examples",
      input_data_gcs_path: "github-issue-summarization-data/github-issues.zip",
      output_model_gcs_bucket: "kubeflow-examples",
      output_model_gcs_path: "github-issue-summarization-data",
      sample_size: "100000",
      gcpSecretName: "user-gcp-sa",
      gcpSecretFile: "user-gcp-sa.json",
    },
    "kubeflow-core": {
      AmbassadorImage: "quay.io/datawire/ambassador:0.30.1",
      AmbassadorServiceType: "ClusterIP",
      StatsdImage: "quay.io/datawire/statsd:0.30.1",
      centralUiImage: "gcr.io/kubeflow-images-public/centraldashboard:v20180618-v0.2.0-rc.0-5-g715aafc8-e3b0c4",
      cloud: "null",
      disks: "null",
      jupyterHubAuthenticator: "null",
      jupyterHubImage: "gcr.io/kubeflow/jupyterhub-k8s:v20180531-3bb991b1",
      jupyterHubServiceType: "ClusterIP",
      jupyterNotebookPVCMount: "/home/jovyan",
      jupyterNotebookRegistry: "gcr.io",
      jupyterNotebookRepoName: "kubeflow-images-public",
      name: "kubeflow-core",
      namespace: "null",
      reportUsage: "false",
      tfDefaultImage: "null",
      tfJobImage: "gcr.io/kubeflow-images-public/tf_operator:v0.2.0",
      tfJobUiServiceType: "ClusterIP",
      tfJobVersion: "v1alpha2",
      usageId: "unknown_cluster",
    },
    "tensor2tensor-v1alpha2": {
      name: "tensor2tensor-v1alpha2",
    },
    "data-downloader": {},
    "tfjob-pvc-v1alpha2": {
      name: "tfjob-pvc-v1alpha2",
    },
    "hp-tune": {},
  },
}
