local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.notebooks;

local notebooks = import "kubeflow/jupyter/notebooks.libsonnet";
local instance = notebooks.new(env, params);
instance.list(instance.all)
