local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.jupyter;

local jupyter = import "kubeflow/jupyter/jupyter.libsonnet";
local instance = jupyter.new(env, params);
instance.list(instance.all)
