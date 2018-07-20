local tfJob = import "kubeflow/tf-job/tf-job.libsonnet";
local baseParams = std.extVar("__ksonnet/params").components["t2t-job"];

{
  getGcloudAuthCmd()::
    [
      "/root/google-cloud-sdk/bin/gcloud",
      "auth",
      "activate-service-account",
      "--key-file",
      "$GOOGLE_APPLICATION_CREDENTIALS",
    ],

  getGsUtilCmd(src_dir, dst_dir)::
    [
      "/root/google-cloud-sdk/bin/gsutil",
      "cp",
      "-r",
      src_dir,
      dst_dir,
    ],

  wrapGsUtil(cmd, params):: {
    local resultCmd =
      (if params.gsDataDir == "null" && params.gsOutputDir == "null" then [] else $.getGcloudAuthCmd() + ["&&"]) +
      (if params.gsDataDir == "null" then [] else $.getGsUtilCmd(params.gsDataDir, params.dataDir) + ["&&"]) +
      cmd +
      (if params.gsOutputDir == "null" then [] else ["&&"] + $.getGsUtilCmd(params.outputDir, params.gsOutputDir)),
    result: ["-c", std.join(" ", resultCmd)]
  }.result,

  getDatagenCmd(params)::
    [
      "t2t-datagen",
      "--problem=" + params.problem,
      "--data_dir=" + params.dataDir,
    ],

  getExporterCmd(params)::
    [
      "t2t-exporter",
      "--problem=" + params.problem,
      "--data_dir=" + params.dataDir,
      "--output_dir=" + params.outputDir,
      "--model=" + params.model,
      "--hparams_set=" + params.hparams_set,
    ],

  getTrainerCmd(params):: {
      local trainer = [
        "t2t-trainer",
        "--generate_data",
        "--problem=" + params.problem,
        "--data_dir=" + params.dataDir,
        "--output_dir=" + params.outputDir,
        "--model=" + params.model,
        "--hparams_set=" + params.hparams_set,
        "--train_steps=" + std.toString(params.train_steps),
      ],

      local workerBase = trainer + [
        "--schedule=train",
        "--ps_gpu=" + std.toString(params.numPsGpu),
        "--worker_gpu=" + std.toString(params.numWorkerGpu),
        "--worker_replicas=" + std.toString(params.numWorker + params.numMaster),
        "--ps_replicas=" + std.toString(params.numPs),
        "--eval_steps=" + std.toString(params.eval_steps),
      ],

      ps: trainer + [
        "--schedule=run_std_server",
        "--ps_job=/job:ps",
      ],

      worker: workerBase + [
        "--worker_job=/job:worker",
      ],

      master: workerBase + [
        "--worker_job=/job:master",
      ],
  },

  tfJobReplica(replicaType, number, args, image, numGpus=0, imagePullSecrets=[], env=[], volumes=[], volumeMounts=[])::
    local containerSpec = {
      image: image,
      name: "tensorflow",
      [if std.length(args) > 0 then "args"]: args,
      [if numGpus > 0 then "resources"]: {
        limits: {
          "nvidia.com/gpu": numGpus,
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
          restartPolicy: "OnFailure",
        },
      },
      tfReplicaType: replicaType,
    },

  parts(newParams, env):: {
    local params = baseParams + newParams,

    local terminationPolicy = if params.numMaster == 1
                              then tfJob.parts.tfJobTerminationPolicy("MASTER", 0)
                              else tfJob.parts.tfJobTerminationPolicy("WORKER", 0),

    local workerImage = if params.numWorkerGpu > 0 then params.imageGpu else params.image,
    local workerImagePullSecrets = [
      { name: "gcp-registry-credentials" },
    ],
    local workerEnv = [
      {
        name: "GOOGLE_APPLICATION_CREDENTIALS",
        value: "/secret/gcp-credentials/key.json"
      },
    ],
    local workerVolumes = [
      {
        name: "gcp-credentials",
        secret: {
          secretName: "gcp-credentials",
        },
      },
    ],
    local workerVolumeMounts = [
      {
        mountPath: "/secret/gcp-credentials",
        name: "gcp-credentials",
      },
    ],

    // TODO(sanyamkapoor): A workaround for tensorflow/tensor2tensor#879
    // once fixed, simply get rid of $.wrapGsUtil method
    local cmd = $.getTrainerCmd(params),
    local finalCmd = {
      master: $.wrapGsUtil(["/usr/local/sbin/t2t-entrypoint"] + cmd.master, params),
      worker: $.wrapGsUtil(["/usr/local/sbin/t2t-entrypoint"] + cmd.worker, params),
      ps: $.wrapGsUtil(["/usr/local/sbin/t2t-entrypoint"] + cmd.ps, params),
    },
    local datagenCmd = $.wrapGsUtil(["/usr/local/sbin/t2t-entrypoint"] + $.getDatagenCmd(params), params),
    local exporterCmd = $.wrapGsUtil(["/usr/local/sbin/t2t-entrypoint"] + $.getExporterCmd(params), params),

    job::
      tfJob.parts.tfJob(
        params.name,
        env.namespace,
        if params.jobType == "datagen" then
          [
            $.tfJobReplica("MASTER", params.numMaster, datagenCmd, workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
          ]
        else if params.jobType == "exporter" then
          [
            $.tfJobReplica("MASTER", params.numMaster, exporterCmd, workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
          ]
        else
          [
            $.tfJobReplica("MASTER", params.numMaster, finalCmd.master, workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
            $.tfJobReplica("WORKER", params.numWorker, finalCmd.worker, workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
            $.tfJobReplica("PS", params.numPs, finalCmd.ps, workerImage, params.numPsGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
          ],
        terminationPolicy
      ),
  },
}
