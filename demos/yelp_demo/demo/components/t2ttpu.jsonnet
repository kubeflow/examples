local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.t2ttpu;
local k = import "k.libsonnet";

local t2ttpu = import "t2ttpu.libsonnet";

std.prune(k.core.v1.list.new([t2ttpu.parts(params, env).job]))
