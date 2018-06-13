local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["t2tcpu"];

// TODO(https://github.com/ksonnet/ksonnet/issues/235): ks param set args won't work if the arg starts with "--".

local k = import "k.libsonnet";
local tfJob = import "kubeflow/tf-job/tf-job.libsonnet";
// updatedParams uses the environment namespace if
// the namespace parameter is not explicitly set
local updatedParams = params {
  namespace: if params.namespace == "null" then env.namespace else params.namespace,
};

local name = params.name;
local namespace = updatedParams.namespace;

local argsParam = params.args;
local args =
  if argsParam == "null" then
    []
  else
    std.split(argsParam, ",");

local image = params.image;
local imageGpu = params.image_gpu;
local imagePullSecrets = params.image_pull_secrets;
local numMasters = params.num_masters;
local numPs = params.num_ps;
local numWorkers = params.num_workers;
local numGpus = params.num_gpus;

local terminationPolicy = if numMasters == 1 then
  tfJob.parts.tfJobTerminationPolicy("MASTER", 0)
else
  tfJob.parts.tfJobTerminationPolicy("WORKER", 0);

local workerSpec = if numGpus > 0 then
  tfJob.parts.tfJobReplica("WORKER", numWorkers, args, imageGpu, imagePullSecrets, numGpus)
else
  tfJob.parts.tfJobReplica("WORKER", numWorkers, args, image, imagePullSecrets);

std.prune(k.core.v1.list.new([
  tfJob.parts.tfJob(
    name,
    namespace,
    [
      tfJob.parts.tfJobReplica("MASTER", numMasters, args, image, imagePullSecrets),
      workerSpec,
      tfJob.parts.tfJobReplica("PS", numPs, args, image, imagePullSecrets),
    ],
    terminationPolicy
  ),
]))
