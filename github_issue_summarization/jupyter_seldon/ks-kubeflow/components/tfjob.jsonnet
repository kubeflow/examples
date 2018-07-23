local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.tfjob;
local k = import "k.libsonnet";

local tfjob = import "tfjob.libsonnet";

std.prune(k.core.v1.list.new([tfjob.parts(params)]))
