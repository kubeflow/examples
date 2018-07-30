local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["tf-training-job"];

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;
local image = params.image;
local numWorkers = params.numWorkers;
local numPs = params.numPs;
local mountPath = params.mountPath;
local pvc = params.pvc;
local pipelineConfigPath = params.pipelineConfigPath;
local trainDir = params.trainDir;
local numGpu = params.numGpu;

local tfjob_cpu = {
  apiVersion: "kubeflow.org/v1alpha2",
  kind: "TFJob",
  metadata: {
    name: name,
    namespace: namespace,
  },
  spec: {
    tfReplicaSpecs: {
      Worker: {
        replicas: numWorkers,
        template: {
          spec: {
            containers: [
              {
                workingDir: "/models",
                command: [
                  "python",
                  "research/object_detection/train.py",
                ],
                args:[
                  "--logstostderr",
                  "--pipeline_config_path=" + pipelineConfigPath,
                  "--train_dir=" + trainDir,
                ],
                image: image,
                name: "tensorflow",
                [if numGpu > 0 then "resources"] : {
                  limits:{
                    "nvidia.com/gpu": numGpu,
                  },
                },
                volumeMounts: [{
                  mountPath: mountPath,
                  name: "pets-data",
                },],
              },
            ],
            volumes: [{
                name: "pets-data",
                persistentVolumeClaim: {
                  claimName: pvc,
                },
            },],
            restartPolicy: "OnFailure",
          },
        },
      },
      Ps: {
        replicas: numPs,
        template: {
          spec: {
            containers: [
              {
                workingDir: "/models",
                command: [
                  "python",
                  "research/object_detection/train.py",
                ],
                args:[
                  "--logstostderr",
                  "--pipeline_config_path=" + pipelineConfigPath,
                  "--train_dir=" + trainDir,
                ],
                image: image,
                name: "tensorflow",
                [if numGpu > 0 then "resources"] : {
                  limits:{
                    "nvidia.com/gpu": numGpu,
                  },
                },
                volumeMounts: [{
                  mountPath: mountPath,
                  name: "pets-data",
                },],
              },
            ],
            volumes: [{
                name: "pets-data",
                persistentVolumeClaim: {
                  claimName: pvc,
                },
            },],
            restartPolicy: "OnFailure",
          },
        },
        tfReplicaType: "PS",
      },
    },
  },
};

k.core.v1.list.new([
  tfjob_cpu,
])