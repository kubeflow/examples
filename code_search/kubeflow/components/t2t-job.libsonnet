local baseParams = std.extVar("__ksonnet/params").components["t2t-job"];

{
  getDatagenCmd(params)::
    [
      "/usr/local/sbin/t2t-entrypoint",
      "t2t-datagen",
      "--problem=" + params.problem,
      "--data_dir=" + params.dataDir,
    ],

  getExporterCmd(params)::
    [
      "/usr/local/sbin/t2t-entrypoint",
      "t2t-exporter",
      "--problem=" + params.problem,
      "--data_dir=" + params.dataDir,
      "--output_dir=" + params.outputDir,
      "--model=" + params.model,
      "--hparams_set=" + params.hparams_set,
    ],

  getTrainerCmd(params):: {
      local trainer = [
        "/usr/local/sbin/t2t-entrypoint",
        "t2t-trainer",
        "--problem=" + params.problem,
        "--model=" + params.model,
        "--hparams_set=" + params.hparams_set,
        "--data_dir=" + params.dataDir,
        "--output_dir=" + params.outputDir,
        "--train_steps=" + std.toString(params.train_steps),
        "--eval_steps=" + std.toString(params.eval_steps),
        "--t2t_usr_dir=/app/code_search/t2t",
      ],

      worker: trainer,

      worker_dist: trainer + [
        "--schedule=train",
        "--ps_gpu=" + std.toString(params.numPsGpu),
        "--worker_gpu=" + std.toString(params.numWorkerGpu),
        "--worker_replicas=" + std.toString(params.numWorker),
        "--ps_replicas=" + std.toString(params.numPs),
        "--eval_steps=" + std.toString(params.eval_steps),
        "--worker_job=/job:worker",
      ],

      ps: trainer + [
        "--schedule=run_std_server",
        "--ps_job=/job:ps",
      ],
  },

  tfJobReplica(replicaType, number, args, image, numGpus=0, imagePullSecrets=[], env=[], volumes=[], volumeMounts=[])::
    local containerSpec = {
      image: image,
      name: "tensorflow",
      [if std.length(args) > 0 then "args"]: args,
      resources: {
        limits: {
          [if numGpus > 0 then "nvidia.com/gpu"]: numGpus,
        },
      },
      [if std.length(env) > 0 then "env"]: env,
      [if std.length(volumeMounts) > 0 then "volumeMounts"]: volumeMounts,
    };
    {
      replicas: number,
      template: {
        spec: {
          containers: [ containerSpec ],
          [if std.length(imagePullSecrets) > 0 then "imagePullSecrets"]: imagePullSecrets,
          [if std.length(volumes) > 0 then "volumes"]: volumes,
          // restartPolicy: "OnFailure",
        },
      },
    },

  parts(newParams, env):: {
    local params = baseParams + newParams,

    local workerImage = if params.numWorkerGpu > 0 then params.imageGpu else params.image,
    local workerEnv = [
      {
        name: "GOOGLE_APPLICATION_CREDENTIALS",
        value: "/secret/gcp-credentials/user-gcp-sa.json"
      },
    ],
    local workerVolumes = [
      {
        name: "gcp-credentials",
        secret: {
          secretName: "user-gcp-sa",
        },
      },
    ],
    local workerVolumeMounts = [
      {
        mountPath: "/secret/gcp-credentials",
        name: "gcp-credentials",
      },
    ],

    local cmd = $.getTrainerCmd(params),
    local workerCmd = if params.jobType == "exporter" then $.getExporterCmd(params)
                      else if params.jobType == "datagen" then $.getDatagenCmd(params)
                      else cmd.worker,

    job:: {
      apiVersion: "kubeflow.org/v1alpha2",
      kind: "TFJob",
      metadata: {
        name: params.name,
        namespace: env.namespace,
      },
      spec: {
        tfReplicaSpecs: {
          [if params.numPs > 0 then "PS"]: $.tfJobReplica("PS", params.numPs, cmd.ps, workerImage,
                                                          numGpus=params.numPsGpu,
                                                          env=workerEnv,
                                                          volumes=workerVolumes,
                                                          volumeMounts=workerVolumeMounts),
          [if params.numWorker > 0 then "Worker"]: $.tfJobReplica("WORKER", params.numWorker,
                                                                  workerCmd, workerImage,
                                                                  numGpus=params.numPsGpu,
                                                                  env=workerEnv,
                                                                  volumes=workerVolumes,
                                                                  volumeMounts=workerVolumeMounts),
        },
      },
    },
  },
}
