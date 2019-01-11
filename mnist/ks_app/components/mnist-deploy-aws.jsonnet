local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["mnist-deploy-aws"];

local k = import "k.libsonnet";
local deployment = k.apps.v1beta1.deployment;
local container = deployment.mixin.spec.template.spec.containersType;

local util = import "kubeflow/tf-serving/util.libsonnet";
local tfserving = import "kubeflow/tf-serving/tf-serving-template.libsonnet";

local base = tfserving.new(env, params);
local tfDeployment = base.tfDeployment +
                     deployment.mapContainers(
                       function(c) {
                         result::
                           c + container.withEnvMixin(
                             if util.toBool(params.s3Enable) then (
                               [
                                 {
                                   name: "AWS_ACCESS_KEY_ID",
                                   valueFrom: { secretKeyRef: { name: params.s3SecretName, key: params.s3SecretAccesskeyidKeyName } },
                                 },
                                 {
                                   name: "AWS_SECRET_ACCESS_KEY",
                                   valueFrom: { secretKeyRef: { name: params.s3SecretName, key: params.s3SecretSecretaccesskeyKeyName } },
                                 },
                                 { name: "AWS_REGION", value: params.s3AwsRegion },
                                 { name: "S3_USE_HTTPS", value: std.toString(params.s3UseHttps) },
                                 { name: "S3_VERIFY_SSL", value: std.toString(params.s3VerifySsl) },
                                 { name: "S3_ENDPOINT", value: params.s3Endpoint },
                               ]
                             ) else [],
                           ),
                       }.result,
                     );
util.list([
  tfDeployment,
  base.tfservingConfig,
],)
