local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["decompress-data-job"];

local k = import "k.libsonnet";
local obj_detection = import "obj-detection.libsonnet";

local namespace = env.namespace;
local jobName = params.name;
local pvc = params.pvc;
local pathToDataset = params.pathToDataset;
local pathToAnnotations = params.pathToAnnotations;
local pathToModel = params.pathToModel;
local mountPath = params.mountPath;

std.prune(k.core.v1.list.new([
obj_detection.decompress_job(namespace, jobName + "-dataset", pvc, pathToDataset, mountPath),
obj_detection.decompress_job(namespace, jobName + "-annotations", pvc, pathToAnnotations, mountPath),
obj_detection.decompress_job(namespace, jobName + "-model", pvc, pathToModel, mountPath)]))