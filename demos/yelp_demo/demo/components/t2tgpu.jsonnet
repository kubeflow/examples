local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.t2tgpu;
local k = import "k.libsonnet";

local t2tgpu = import "t2tgpu.libsonnet";

std.prune(k.core.v1.list.new([t2tgpu.parts(params, env).job]))
