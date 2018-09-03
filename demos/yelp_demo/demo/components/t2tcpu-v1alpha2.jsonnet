local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["t2tcpu-v1alpha2"];

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;

local updatedParams = {
  cloud: "gke",

  sync: "0",

  dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
  usrDir: "./yelp_sentiment",
  problem: "yelp_sentiment",

  model: "transformer_encoder",
  hparams: "transformer_yelp_sentiment",
  hparamsSet: "transformer_yelp_sentiment",

  outputGCSPath: "gs://kubeflow-demo-base/kubeflow-demo-base-demo/CPU/training/yelp-model",

  gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",
  cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",

  trainSteps: 1000,
  evalSteps: 10,

  psGpu: 0,
  workerGpu: 0,

  workers: 3,
  masters: 1,
  ps: 1,

  jobName: "t2tcpu",
} + params;

local containerEnv = [
  {
    name: "PYTHONPATH",
    value: "/home/jovyan",
  },
];

local baseCommand = [
  "bash",
  "/home/jovyan/yelp_sentiment/worker_launcher.sh",
  "--train_steps=" + updatedParams.trainSteps,
  "--hparams_set=" + updatedParams.hparams,
  "--model=" + updatedParams.model,
  "--problem=" + updatedParams.problem,
  "--t2t_usr_dir=" + updatedParams.usrDir,
  "--data_dir=" + updatedParams.dataDir,
  "--output_dir=" + updatedParams.outputGCSPath,
];

local psCommand = baseCommand + [
  "--schedule=run_std_server",
];

local totalWorkerReplicas = updatedParams.workers + updatedParams.masters;

local workerBaseCommand = baseCommand + [
  "--schedule=train",
  "--sync=" + updatedParams.sync,
  "--ps_gpu=" + updatedParams.psGpu,
  "--worker_gpu=" + updatedParams.workerGpu,
  "--worker_replicas=" + totalWorkerReplicas,
  "--ps_replicas=" + updatedParams.ps,
  "--eval_steps=" + updatedParams.evalSteps,
];

local workerCommand = workerBaseCommand + [
  "--worker_job=/job:worker",
];

local masterCommand = workerBaseCommand + [
  "--worker_job=/job:master",
];

local cloud = std.toString(updatedParams.cloud);

local tfjob = {
  apiVersion: "kubeflow.org/v1alpha2",
  kind: "TFJob",
  metadata: {
    name: updatedParams.jobName,
    namespace: namespace,
  },
  spec: {
    tfReplicaSpecs: {
      Master: {
        replicas: 1,
        template: {
              spec: {
                containers: [
                  {
                    command: masterCommand,
                    image: if updatedParams.workerGpu > 0 then updatedParams.gpuImage else updatedParams.cpuImage,
                    name: "tensorflow",
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
                    command: workerCommand,
                    image: if updatedParams.workerGpu > 0 then updatedParams.gpuImage else updatedParams.cpuImage,
                    name: "tensorflow",
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
                    command: psCommand,
                    image: updatedParams.cpuImage,
                    name: "tensorflow",
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



