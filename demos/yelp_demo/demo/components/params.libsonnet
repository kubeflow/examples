{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "kubeflow-core": {
      AmbassadorImage: "quay.io/datawire/ambassador:0.30.1",
      AmbassadorServiceType: "ClusterIP",
      StatsdImage: "quay.io/datawire/statsd:0.30.1",
      centralUiImage: "gcr.io/kubeflow-images-public/centraldashboard:v20180618-v0.2.0-rc.0-5-g715aafc8-e3b0c4",
      cloud: "gke",
      disks: "null",
      jupyterHubAuthenticator: "null",
      jupyterHubImage: "gcr.io/kubeflow/jupyterhub-k8s:v20180531-3bb991b1",
      jupyterHubServiceType: "ClusterIP",
      jupyterNotebookPVCMount: "null",
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
    "t2tcpu": {
      workerGpu: 0,
      cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",
      dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
      gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",
      outputGCSPath: "gs://kubeflow-demo-base/kubeflow-demo-base-demo/CPU/training/yelp-model",
    },
    "t2tcpu-v1alpha2": {
      workerGpu: 0,
      cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",
      dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
      gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",
      outputGCSPath: "gs://kubeflow-demo-base/kubeflow-demo-base-demo/CPU/training/yelp-model",
    },
    "t2tgpu": {
      workerGpu: 1,
      cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",
      dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
      gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",
      outputGCSPath: "gs://kubeflow-demo-base/kubeflow-demo-base-demo/GPU/training/yelp-model",
    },
    "t2ttpu": {
      cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",
      dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
      gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",
      outputGCSPath: "gs://kubeflow-demo-base/kubeflow-demo-base-demo/TPU/training/yelp-model",
    },
    "serving": {
      modelPath: "gs://kubeflow-demo-base/kubeflow-demo-base-demo/TPU/training/yelp-model/export/Servo",
      deployHttpProxy: "true",
      modelServerImage: "gcr.io/kubeflow-images-public/tf-model-server-cpu:v20180523-2a68f293",
      name: "serving"
    },
    "cert-manager": {
      acmeEmail: "google-kubeflow-team@google.com",
      acmeUrl: "https://acme-v01.api.letsencrypt.org/directory",
      name: "cert-manager",
      namespace: "kubeflow",
    },
    "iap-ingress": {
      disableJwtChecking: "false",
      envoyImage: "gcr.io/kubeflow-images-staging/envoy:v20180309-0fb4886b463698702b6a08955045731903a18738",
      hostname: "kubecon-keynote-demo.kubeflow.dev",
      ipName: "static-ip",
      issuer: "letsencrypt-prod",
      name: "iap-ingress",
      namespace: "kubeflow",
      oauthSecretName: "kubeflow-oauth",
      secretName: "envoy-ingress-tls",
    },
    "ui": {
      image: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-ui:latest",
    },
  },
}
