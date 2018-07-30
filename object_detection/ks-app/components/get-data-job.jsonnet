local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["get-data-job"];

local k = import "k.libsonnet";
local obj_detection = import "obj-detection.libsonnet";

local namespace = env.namespace;
local jobName = params.name;
local pvc = params.pvc;
local urlData = params.urlData;
local urlAnnotations = params.urlAnnotations;
local urlModel = params.urlModel;
local urlPipelineConfig = params.urlPipelineConfig;
local mountPath = params.mountPath;

std.prune(k.core.v1.list.new([
  obj_detection.get_data_job(namespace, jobName + "-dataset", pvc, urlData, mountPath),
  obj_detection.get_data_job(namespace, jobName + "-annotations", pvc, urlAnnotations, mountPath),
  obj_detection.get_data_job(namespace, jobName + "-model", pvc, urlModel, mountPath),
  obj_detection.get_data_job(namespace, jobName + "-config", pvc, urlPipelineConfig, mountPath)]))