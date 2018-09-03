local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["t2tcpu-v1alpha1"];
local k = import "k.libsonnet";

local t2tcpu = import "t2tcpu-v1alpha1.libsonnet";

std.prune(k.core.v1.list.new([t2tcpu.parts(params, env).job]))
