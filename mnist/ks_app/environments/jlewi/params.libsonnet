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
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}