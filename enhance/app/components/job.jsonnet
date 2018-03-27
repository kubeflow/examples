local k = import "k.libsonnet";

local params = std.extVar("__ksonnet/params").components["datagen"];

local jobLib = import "job.libsonnet";

local job = jobLib.parts.job(params.name, params.namespace, params.image, params.command, params.restartPolicy, params.backoffLimit);

std.prune(k.core.v1.list.new([job]))