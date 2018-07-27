// @apiVersion 0.1
// @name io.ksonnet.pkg.get-data-job
// @description K8s get data from remote url job
// @shortDescription A K8s job to get data from remote url
// @param name string Name to give to each of the components
// @param pvc string Name of the PVC
// @param mountPath string Path to mount the PVC
// @param urlData string Remote URL where the data is located
// @param urlAnnotations string Remote URL where the annotations are located
// @param urlModel string Remote URL where the model is located
// @param urlPipelineConfig string Remote URL where the pipeline config is located

local k = import "k.libsonnet";
local obj_detection = import "objectDetection/obj-detection/obj-detection.libsonnet";

local namespace = env.namespace;
local jobName = import 'param://name';
local pvc = import 'param://pvc';
local urlData = import 'param://urlData';
local urlAnnotations = import 'param://urlAnnotations';
local urlModel = import 'param://urlModel';
local urlPipelineConfig = import 'param://urlPipelineConfig';
local mountPath = import 'param://mountPath';

std.prune(k.core.v1.list.new([
  obj_detection.get_data_job(namespace, jobName + "-dataset", pvc, urlData, mountPath),
  obj_detection.get_data_job(namespace, jobName + "-annotations", pvc, urlAnnotations, mountPath),
  obj_detection.get_data_job(namespace, jobName + "-model", pvc, urlModel, mountPath),
  obj_detection.get_data_job(namespace, jobName + "-config", pvc, urlPipelineConfig, mountPath)]))