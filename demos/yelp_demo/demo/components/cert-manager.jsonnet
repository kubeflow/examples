local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["cert-manager"];
// TODO(https://github.com/ksonnet/ksonnet/issues/222): We have to add namespace as an explicit parameter
// because ksonnet doesn't support inheriting it from the environment yet.

local k = import "k.libsonnet";
local certManager = import "kubeflow/core/cert-manager.libsonnet";

local name = params.name;
local acmeEmail = params.acmeEmail;
local acmeUrl = params.acmeUrl;

// updatedParams uses the environment namespace if
// the namespace parameter is not explicitly set
local updatedParams = params {
  namespace: if params.namespace == "null" then env.namespace else params.namespace
};

certManager.parts(updatedParams.namespace).certManagerParts(acmeEmail, acmeUrl)
