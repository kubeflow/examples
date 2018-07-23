local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.seldon;
local k = import "k.libsonnet";
local core = import "kubeflow/seldon/core.libsonnet";

// updatedParams uses the environment namespace if
// the namespace parameter is not explicitly set
local updatedParams = params {
  namespace: if params.namespace == "null" then env.namespace else params.namespace,
};

local name = params.name;
local namespace = updatedParams.namespace;
local withRbac = params.withRbac;
local withApife = params.withApife;

// APIFE
local apifeImage = params.apifeImage;
local apifeServiceType = params.apifeServiceType;

// Cluster Manager (The CRD Operator)
local operatorImage = params.operatorImage;
local operatorSpringOptsParam = params.operatorSpringOpts;
local operatorSpringOpts = if operatorSpringOptsParam != "null" then operatorSpringOptsParam else "";
local operatorJavaOptsParam = params.operatorJavaOpts;
local operatorJavaOpts = if operatorJavaOptsParam != "null" then operatorJavaOptsParam else "";

// Engine
local engineImage = params.engineImage;

// APIFE
local apife = [
  core.parts(namespace).apife(apifeImage, withRbac),
  core.parts(namespace).apifeService(apifeServiceType),
];

local rbac = [
  core.parts(namespace).rbacServiceAccount(),
  core.parts(namespace).rbacClusterRoleBinding(),
];

// Core
local coreComponents = [
  core.parts(namespace).deploymentOperator(engineImage, operatorImage, operatorSpringOpts, operatorJavaOpts, withRbac),
  core.parts(namespace).redisDeployment(),
  core.parts(namespace).redisService(),
  core.parts(namespace).crd(),
];

if withRbac == "true" && withApife == "true" then
  k.core.v1.list.new(apife + rbac + coreComponents)
else if withRbac == "true" && withApife == "false" then
  k.core.v1.list.new(rbac + coreComponents)
else if withRbac == "false" && withApife == "true" then
  k.core.v1.list.new(apife + coreComponents)
else if withRbac == "false" && withApife == "false" then
  k.core.v1.list.new(coreComponents)
