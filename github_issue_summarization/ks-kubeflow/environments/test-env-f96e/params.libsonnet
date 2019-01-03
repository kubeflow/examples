local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    "tfjob-v1beta1"+: {
      name: 'jlewi-gis-test',
      namespace: 'kubeflow',
      num_epochs: 1,
      sample_size: 10,
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}