local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    "tfjob-v1alpha2"+: {
      output_model_gcs_bucket: 'kubecon-gh-demo',
      output_model_gcs_path: 'gh-demo/20181008/output',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}