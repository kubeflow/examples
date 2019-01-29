local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.openvino;

local openvino = import "kubeflow/openvino/openvino.libsonnet";
local instance = openvino.new(env, params);
instance.list(instance.all)
