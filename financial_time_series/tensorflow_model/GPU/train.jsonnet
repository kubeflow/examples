local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.train;

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;
local image = params.image;

local argsParam = params.args;
local args =
  if argsParam == "null" then
    []
  else
    std.split(argsParam, ",");

local tfjob = {
  apiVersion: "kubeflow.org/v1alpha2",
  kind: "TFJob",
  metadata: {
    name: name,
    namespace: namespace,
  },
  spec: {
    tfReplicaSpecs: {
      Worker: {
        replicas: 1,
        template: {
          spec: {
            containers: [
              {
                args: args,
                image: if params.num_gpu > 0 then params.gpuImage else params.cpuImage,
                name: "tensorflow",
                [if params.num_gpu > 0 then "resources"]: {
                  limits: {
                    "nvidia.com/gpu": params.num_gpu,
                  },
                },
                workingDir: "/opt/workdir",
              },
            ],
            restartPolicy: "OnFailure",
          },
        },
      },
    },
  },
};

k.core.v1.list.new([
  tfjob,
])
