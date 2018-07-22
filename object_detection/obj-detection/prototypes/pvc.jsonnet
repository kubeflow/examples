// @apiVersion 0.1
// @name io.ksonnet.pkg.pvc
// @description create a PVC
// @shortDescription A K8s Persistent Volume Claim
// @param name string Name to give to each of the components
// @param storage string The storage limit for the PVC
// @param accessMode string The access mode for the PVC

local k = import "k.libsonnet";
local obj_detection = import "objectDetection/obj-detection/obj-detection.libsonnet";

local namespace = env.namespace;
local pvcName = import 'param://name';
local storage = import 'param://storage';
local accessMode = import 'param://accessMode';

std.prune(k.core.v1.list.new(obj_detection.pvc(namespace, pvcName, storage, accessMode)))