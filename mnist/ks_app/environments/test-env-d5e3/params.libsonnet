local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    train+: {
      name: 'jlewi-deploy-test',
      namespace: 'jlewi',
      modelBasePath: 'gs://kubeflow-ci_temp/mnist-jlewi/export',
    },
    "mnist-deploy-gcp"+: {
      name: 'jlewi-deploy-test',
      namespace: 'jlewi',
      modelBasePath: 'gs://kubeflow-ci_temp/mnist-jlewi/export',
    },
    "mnist-service"+: {
      name: 'jlewi-deploy-test',
      namespace: 'jlewi',
      modelBasePath: 'gs://kubeflow-ci_temp/mnist-jlewi/export',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}