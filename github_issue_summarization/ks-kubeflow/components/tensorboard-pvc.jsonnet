local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["tensorboard-pvc"];
local k = import "k.libsonnet";

// We define it in a .libsonnet file as a giant work around for
// https://github.com/ksonnet/ksonnet/issues/670
// We should be able to get rid of this once we go to 0.12
local tb = import "tensorboard-pvc.libsonnet";


std.prune(k.core.v1.list.new([tb.parts(params, env).service, tb.parts(params, env).deployment]))
