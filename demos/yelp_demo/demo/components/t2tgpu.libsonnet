{
  parts(params, env):: {
    // Define some defaults.
    local updatedParams = {
      sync: "0",

      dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
      usrDir: "./yelp_sentiment",
      problem: "yelp_sentiment",

      model: "transformer_encoder",
      hparams: "transformer_yelp_sentiment",
      hparamsSet: "transformer_yelp_sentiment",

      outputGCSPath: "gs://kubeflow-demo-base/training/yelp-model-GPU",

      gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",
      cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",

      trainSteps: 1000,
      evalSteps: 10,

      psGpu: 0,
      workerGpu: 1,

      workers: 3,
      masters: 1,
      ps: 1,

      jobName: "t2tgpu",
    } + params,

    local baseCommand = [
      "bash",
      "/home/jovyan/yelp_sentiment/worker_launcher.sh",
      "--train_steps=" + std.toString(updatedParams.trainSteps),
      "--hparams_set=" + updatedParams.hparams,
      "--model=" + updatedParams.model,
      "--problem=" + updatedParams.problem,
      "--t2t_usr_dir=" + updatedParams.usrDir,
      "--data_dir=" + updatedParams.dataDir,
      "--output_dir=" + updatedParams.outputGCSPath,
    ],
    local psCommand = baseCommand + [
      "--schedule=run_std_server",
    ],
    local workerBaseCommand = baseCommand + [
      "--schedule=train",
      "--sync=" + std.toString(updatedParams.sync),
      "--ps_gpu=" + std.toString(updatedParams.psGpu),
      "--worker_gpu=" + std.toString(updatedParams.workerGpu),
      "--worker_replicas=" + std.toString(updatedParams.workers + updatedParams.masters),
      "--ps_replicas=" + std.toString(updatedParams.ps),
      "--eval_steps=" + std.toString(updatedParams.evalSteps),
    ],
    local workerCommand = workerBaseCommand + [
      "--worker_job=/job:worker",
    ],
    local masterCommand = workerBaseCommand + [
      "--worker_job=/job:master",
    ],
    local namespace = env.namespace,

    job:: {
      apiVersion: "kubeflow.org/v1alpha1",
      kind: "TFJob",
      metadata: {
        name: updatedParams.jobName,
        namespace: env.namespace,
      },
      spec: {
        replicaSpecs: [
          {
            replicas: 1,
            template: {
              spec: {
                containers: [
                  {
                    image: if updatedParams.workerGpu > 0 then updatedParams.gpuImage else updatedParams.cpuImage,
                    name: "tensorflow",
                    command: masterCommand,
                    resources: {
                      limits: {
                        cpu: "1",
                        [if updatedParams.workerGpu > 0 then "nvidia.com/gpu"]: updatedParams.workerGpu,
                      },
                    },
                  },
                ],
                restartPolicy: "OnFailure",
              },
            },
            tfReplicaType: "MASTER",
          },
          {
            replicas: updatedParams.workers,
            template: {
              spec: {
                containers: [
                  {
                    image: if updatedParams.workerGpu > 0 then updatedParams.gpuImage else updatedParams.cpuImage,
                    name: "tensorflow",
                    command: workerCommand,
                    resources: {
                      limits: {
                        cpu: "1",
                        [if updatedParams.workerGpu > 0 then "nvidia.com/gpu"]: updatedParams.workerGpu,
                      },
                    },
                  },
                ],
                restartPolicy: "OnFailure",
              },
            },
            tfReplicaType: "WORKER",
          },
          {
            replicas: updatedParams.ps,
            template: {
              spec: {
                containers: [
                  {
                    command: psCommand,
                    image: updatedParams.cpuImage,
                    name: "tensorflow",
                    resources: {
                      limits: {
                        cpu: "1",
                      },
                    },
                  },
                ],
                restartPolicy: "OnFailure",
              },
            },
            tfReplicaType: "PS",
          },
        ],
        terminationPolicy: {
          chief: {
            replicaIndex: 0,
            replicaName: "MASTER",
          },
        },
      },
    },  // job
  },  //parts
}
