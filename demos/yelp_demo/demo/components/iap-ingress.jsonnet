local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["iap-ingress"];
local k = import "k.libsonnet";
local iap = import "kubeflow/core/iap.libsonnet";
local util = import "kubeflow/core/util.libsonnet";

// updatedParams uses the environment namespace if
// the namespace parameter is not explicitly set
local updatedParams = params {
  namespace: if params.namespace == "null" then env.namespace else params.namespace
};

local name = params.name;
local namespace = updatedParams.namespace;
local secretName = params.secretName;
local ipName = params.ipName;
local hostname = params.hostname;
local issuer = params.issuer;
local envoyImage = params.envoyImage;
local disableJwtCheckingParam = params.disableJwtChecking;
local disableJwtChecking = util.toBool(disableJwtCheckingParam);
local oauthSecretName = params.oauthSecretName;

iap.parts(namespace).ingressParts(secretName, ipName, hostname, issuer, envoyImage, disableJwtChecking, oauthSecretName)
