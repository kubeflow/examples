local k = import "k.libsonnet";
local nms = import "nms.libsonnet";

local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["search-index-creator"];

std.prune(k.core.v1.list.new(nms.parts(params, env).creator))
