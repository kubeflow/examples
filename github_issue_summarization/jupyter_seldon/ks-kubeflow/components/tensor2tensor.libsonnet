{
  parts(params, env):: {
    // Define some defaults.
    local updatedParams = {
      sync: "0",
      
      dataDir: "gs://kubeflow-examples-data/gh_issue_summarization/data",
      usrDir: "./github",
      problem: "github_issue_summarization_problem",

      model: "transformer_encoder",
      hparams: "transformer_github_issues",
      hparamsSet: "transformer_github_issues",      
      outputGCSPath: "gs://kubecon-gh-demo/gh-t2t-out/temp",

      gpuImage: null,
      cpuImage: null,

      trainSteps: 20000,
      evalSteps: 10,

      psGpu: 0,
      workerGpu: 0,

      workers: 3,
      masters: 1,
      ps: 1,

      jobName: "tensor2tensor",
    } + params,

    local containerEnv = [
      {
        name: "PYTHONPATH",
        value: "/home/jovyan",
      }
    ],
    local baseCommand = [      
      "/home/jovyan/github/t2t_launcher.sh",
      "--train_steps=" + updatedParams.trainSteps,
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
    local totalWorkerReplicas = updatedParams.workers + updatedParams.masters,
    local workerBaseCommand = baseCommand + [
      "--schedule=train",
      "--sync=" + updatedParams.sync,
      "--ps_gpu=" + updatedParams.psGpu,
      "--worker_gpu=" + updatedParams.workerGpu,
      // We explicitly want to add worker and 
      "--worker_replicas=" + totalWorkerReplicas,
      "--ps_replicas=" + updatedParams.ps,
      "--eval_steps=" + updatedParams.evalSteps,
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
            tfReplicaType: "WORKER",
          },
          {
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
