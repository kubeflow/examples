{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    workflows: {
      bucket: "kubeflow-ci_temp",
      name: "kubeflow-examples-presubmit-test-374-6e32",
      namespace: "kubeflow-test-infra",
      prow: "JOB_NAME=kubeflow-examples-presubmit-test,JOB_TYPE=presubmit,PULL_NUMBER=209,REPO_NAME=examples,REPO_OWNER=kubeflow,BUILD_NUMBER=997a",
      prow_env: "JOB_NAME=kubeflow-examples-presubmit-test,JOB_TYPE=presubmit,PULL_NUMBER=374,REPO_NAME=examples,REPO_OWNER=kubeflow,BUILD_NUMBER=6e32",
    },
    "pytorch-mnist-webui-release": {
      bucket: "kubeflow-releasing-artifacts",
      cluster: "kubeflow-releasing",
      dockerfile: "Dockerfile",
      dockerfileDir: "kubeflow/examples/pytorch_mnist/web-ui",
      extra_args: "null",
      extra_repos: "kubeflow/testing@HEAD",
      gcpCredentialsSecretName: "gcp-credentials",
      image: "pytorch-mnist-webui",
      name: "pytorch-mnist-webui-release",
      namespace: "kubeflow-releasing",
      nfsVolumeClaim: "nfs-external",
      project: "kubeflow-releasing",
      prow_env: "REPO_OWNER=kubeflow,REPO_NAME=kubeflow,PULL_BASE_SHA=master",
      registry: "gcr.io/kubeflow-examples",
      testing_image: "gcr.io/kubeflow-ci/test-worker",
      versionTag: "latest",
      zone: "us-central1-a",
    },
  },
}
