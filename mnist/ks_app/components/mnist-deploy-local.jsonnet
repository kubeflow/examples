local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["mnist-deploy-local"];

local k = import "k.libsonnet";
local deployment = k.apps.v1beta1.deployment;
local container = deployment.mixin.spec.template.spec.containersType;

local util = import "kubeflow/tf-serving/util.libsonnet";
local tfserving = import "kubeflow/tf-serving/tf-serving-template.libsonnet";

local base = tfserving.new(env, params);
local tfDeployment = base.tfDeployment +
                     deployment.mixin.spec.template.spec.withVolumesMixin(
                       if params.pvcName != "null" && params.pvcName != "" then (
                         [{
                           name: "local-storage",
                           persistentVolumeClaim: {
                             claimName: params.pvcName,
                           },
                         }]
                       ) else [],
                     ) +
                     deployment.mapContainers(
                       function(c) {
                         result::
                           c + container.withVolumeMountsMixin(
                             if params.pvcName != "null" && params.pvcName != "" then (
                               [{
                                 name: "local-storage",
                                 mountPath: "/mnt",
                               }]
                             ) else [],
                           ),
                       }.result,
                     );
util.list([
  tfDeployment,
  base.tfservingConfig,
],)
