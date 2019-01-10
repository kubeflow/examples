local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    code_search+: {
      namespace: 'kubeflow-test-infra',
      name: 'jlewi-code-search-test-446-1227-171741',
      prow_env: 'JOB_NAME=code-search-test,JOB_TYPE=presubmit,REPO_NAME=examples,REPO_OWNER=kubeflow,BUILD_NUMBER=1227-171741,BUILD_ID=1227-171741,PULL_NUMBER=446',
    },
    gis+: {
      namespace: 'kubeflow-test-infra',
      name: 'jlewi-gis-search-test-456-0105-104058',
      prow_env: 'JOB_NAME=gis-search-test,JOB_TYPE=presubmit,REPO_NAME=examples,REPO_OWNER=kubeflow,BUILD_NUMBER=0105-104058,BUILD_ID=0105-104058,PULL_NUMBER=456',
    },
    mnist+: {
      namespace: 'kubeflow-test-infra',
      name: 'jlewi-mnist-test-469-0111-081531',
      prow_env: 'JOB_NAME=mnist-test,JOB_TYPE=presubmit,REPO_NAME=examples,REPO_OWNER=kubeflow,BUILD_NUMBER=0111-081531,BUILD_ID=0111-081531,PULL_NUMBER=469',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}