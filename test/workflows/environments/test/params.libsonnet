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
      name: 'jlewi-gis-search-test-456-1230-153310',
      prow_env: 'JOB_NAME=gis-search-test,JOB_TYPE=presubmit,REPO_NAME=examples,REPO_OWNER=kubeflow,BUILD_NUMBER=1230-153310,BUILD_ID=1230-153310,PULL_NUMBER=456',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}