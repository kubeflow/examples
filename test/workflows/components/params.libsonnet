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
  },
}
