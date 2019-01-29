local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.profiles;

local profile = import "kubeflow/profiles/profiles.libsonnet";
local instance = profile.new(env, params);
instance.list(instance.all)
