local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    "mnist-train"+: {
      envVariables: 'GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/user-gcp-sa.json',
    },
    train+: {
      name: 'mnist-train-dist',
      secret: 'user-gcp-sa=/var/secrets',
      numSteps: 10,
      image: 'gcr.io/kubeflow-examples/mnist/model:v20190111-v0.2-146-g0bbff62-dirty-12f353',
      numWorkers: 2,
      numPs: 1,
    },
    "deploy-gcp"+: {
      modelBasePath: 'gs://kubeflow-ci_temp/mnist-jlewi/export',
    },
    "mnist-deploy-gcp"+: {
      modelBasePath: 'gs://kubeflow-ci_temp/mnist-jlewi/export',
      name: 'jlewi-deploy-test',
      namespace: 'jlewi',
    },
    "mnist-service"+: {
      namespace: 'jlewi',
    },
    tensorboard+: {
      logDir: 'gs://kubeflow-ci_temp/mnist-jlewi/',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}