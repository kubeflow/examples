{
  // convert a list of two items into a map representing an environment variable
  // TODO(jlewi): Should we move this into kubeflow/core/util.libsonnet
  listToMap:: function(v)
    {
      name: v[0],
      value: v[1],
    },

  // convert a list of two items into a map representing an env variable referencing k8s secret
  listToSecretMap:: function(v)
    {
      name: v[0],
        valueFrom: {
          secretKeyRef: {
            name: std.split(v[1], ".")[0],
            key: std.split(v[1], ".")[1],
          }
        }
    },

  // Function to turn comma separated list of environment variables into a dictionary.
  parseEnv:: function(v)
    local pieces = std.split(v, ",");
    if v != "" && std.length(pieces) > 0 then
      std.map(
        function(i) $.listToMap(std.split(i, "=")),
        std.split(v, ",")
      )
    else [],

  // Function to turn comma separated list of env variables referencing secrets into a dictionary.
  parseSecrets:: function(v)
    local pieces = std.split(v, ",");
    if v != "" && std.length(pieces) > 0 then
      std.map(
        function(i) $.listToSecretMap(std.split(i, "=")),
        std.split(v, ",")
      )
    else [],
}