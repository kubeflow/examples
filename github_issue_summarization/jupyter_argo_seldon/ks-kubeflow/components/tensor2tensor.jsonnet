local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.tensor2tensor;
local k = import "k.libsonnet";

local tensor2tensor = import "tensor2tensor.libsonnet";

std.prune(k.core.v1.list.new([tensor2tensor.parts(params, env).job]))
