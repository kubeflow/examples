// @apiVersion 0.1
// @name io.ksonnet.pkg.tf-training-job
// @description tf-training-job
// @shortDescription A simple TFJob to run object detection training
// @param name string Name for the job.
// @param image string Image to use for the job.
// @param numWorkers number Number of workers.
// @param numPs number Number of parameter servers.
// @param mountPath string Volume Mount Path
// @param pvc string Persistent volume claim name to use
// @param pipelineConfigPath string Path to the pipeline configuration file
// @param trainDir string Training output directory
// @optionalParam numGpu number 0 Number of GPU resources to use

local k = import "k.libsonnet";

local name = import 'param://name';
local namespace = env.namespace;
local image = import 'param://image';
local numWorkers = import 'param://numWorkers';
local numPs = import 'param://numPs';
local mountPath = import 'param://mountPath';
local pvc = import 'param://pvc';
local pipelineConfigPath = import 'param://pipelineConfigPath';
local trainDir = import 'param://trainDir';
local numGpu = import 'param://numGpu';

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