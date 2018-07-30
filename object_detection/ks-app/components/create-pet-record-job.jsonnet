local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["create-pet-record-job"];

local k = import "k.libsonnet";
local obj_detection = import "obj-detection.libsonnet";

local namespace = env.namespace;
local jobName = params.name;
local pvc = params.pvc;
local mountPath = params.mountPath;
local image = params.image;
local command = params.command;
local args = params.args;

std.prune(k.core.v1.list.new(obj_detection.export_tf_graph_job(namespace, jobName, image, command, args, pvc, mountPath)))