local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["pets-pvc"];

local k = import "k.libsonnet";
local obj_detection = import "obj-detection.libsonnet";

local namespace = env.namespace;
local pvcName = params.name;
local storage = params.storage;
local accessMode = params.accessMode;

std.prune(k.core.v1.list.new(obj_detection.pvc(namespace, pvcName, storage, accessMode)))