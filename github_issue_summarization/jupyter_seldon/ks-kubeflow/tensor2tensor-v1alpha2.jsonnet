local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["tensor2tensor-v1alpha2"];

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;

local tfjob = {
  apiVersion: "kubeflow.org/v1alpha2",
  kind: "TFJob",
  metadata: {
    name: name,
    namespace: namespace,
  },
  spec: {
    tfReplicaSpecs: {
      Master: {
        replicas: updatedParams.workers,
        template: {
              spec: {
                containers: [
                  {
                    image: if updatedParams.workerGpu > 0 then updatedParams.gpuImage else updatedParams.cpuImage,
                    name: "tensorflow",
                    command: masterCommand,
                    env: containerEnv,
                    [if updatedParams.workerGpu > 0 then "resources"]: {
                      limits: {
                        "nvidia.com/gpu": updatedParams.workerGpu,
                      },
                    },
                  },
                ],
                restartPolicy: "OnFailure",
              },
            },
      }, // Master

      Worker: {
        replicas: updatedParams.workers,
        template: {
              spec: {
                containers: [
                  {
                    image: if updatedParams.workerGpu > 0 then updatedParams.gpuImage else updatedParams.cpuImage,
                    name: "tensorflow",
                    command: workerCommand,
                    env: containerEnv,
                    [if updatedParams.workerGpu > 0 then "resources"]: {
                      limits: {
                        "nvidia.com/gpu": updatedParams.workerGpu,
                      },
                    },
                  },
                ],
                restartPolicy: "OnFailure",
              },
            },
      }, // Worker
      Ps: {
        replicas: updatedParams.ps,
        template: {
              spec: {
                containers: [
                  {
                    image: updatedParams.cpuImage,
                    name: "tensorflow",
                    command: psCommand,
                    env: containerEnv,
                  },
                ],
                restartPolicy: "OnFailure",
              },
            }, 
    }, // Ps    
  }, // tfReplicaSpecs
 }, // Spec
}; // tfJob

k.core.v1.list.new([
  tfjob,
])
