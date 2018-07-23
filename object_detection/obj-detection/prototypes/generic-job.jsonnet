// @apiVersion 0.1
// @name io.ksonnet.pkg.generic-job
// @description K8s job export TensorFlow graph
// @shortDescription Exports a TF graph to an specific location in a PVC
// @param name string Name to give to each of the components
// @param image string Docker image to use
// @param command array Command to use
// @param args array command args
// @param pvc string Name of the PVC
// @param mountPath string Path to mount the PVC

local k = import "k.libsonnet";
local obj_detection = import "objectDetection/obj-detection/obj-detection.libsonnet";

local namespace = env.namespace;
local jobName = import 'param://name';
local pvc = import 'param://pvc';
local mountPath = import 'param://mountPath';
local image = import 'param://image';
local command = import 'param://command';
local args = import 'param://args';

std.prune(k.core.v1.list.new(obj_detection.export_tf_graph_job(namespace, jobName, image, command, args, pvc, mountPath)))