local params = std.extVar("__ksonnet/params");
local globals = import "globals.libsonnet";
local envParams = params + {
  components +: {
    "submit-code-embeddings-job"+: {
      // 2 hour in milliseconds
      waitUntilFinishDuration: 7200000,
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals, for x in std.objectFields(envParams.components)
  },
}
