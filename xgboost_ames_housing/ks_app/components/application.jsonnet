local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.application;

local application = import "kubeflow/application/application.libsonnet";
local instance = application.new(env, params);
instance.list(instance.all)
