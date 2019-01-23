{
  // convert a list of two items into a map representing an environment variable
  // TODO(jlewi): Should we move this into kubeflow/core/util.libsonnet
  listToMap:: function(v)
    {
      name: v[0],
      value: v[1],
    },

  // convert a list of two items into a map representing a secret name and key
  listToSecretMap:: function(v)
    {
      name: v[0],
      key: v[1],
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

  // Function to turn comma separated list of secret names and keys into a dictionary.
  parseSecret:: function(v)
    local pieces = std.split(v, ",");
    if v != "" && std.length(pieces) > 0 then
      std.map(
        function(i) $.listToSecretMap(std.split(i, ".")),
        std.split(v, ",")
      )
    else [],
}