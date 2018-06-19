local tfJob = import "kubeflow/tf-job/tf-job.libsonnet";
local baseParams = std.extVar("__ksonnet/params").components["t2t-job"];

{
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
      trainer: [
        "t2t-trainer",
        "--problem=" + params.problem,
        "--data_dir=" + params.dataDir,
        "--output_dir=" + params.outputDir,
        "--model=" + params.model,
        "--hparams_set=" + params.hparams_set,
        "--train_steps=" + std.toString(params.train_steps),
      ],

      workerBase: self.trainer + [
        "--schedule=train",
        "--ps_gpu=" + std.toString(params.numPsGpu),
        "--worker_gpu=" + std.toString(params.numWorkerGpu),
        "--worker_replicas=" + std.toString(params.numWorker + params.numMaster),
        "--ps_replicas=" + std.toString(params.numPs),
        "--eval_steps=" + std.toString(params.eval_steps),
      ],

      ps: self.trainer + [
        "--schedule=run_std_server",
        "--ps_job=/job:ps",
      ],

      worker: self.workerBase + [
        "--worker_job=/job:worker",
      ],

      master: self.workerBase + [
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
    local cmd = $.getTrainerCmd(params),

    job::
      tfJob.parts.tfJob(
        params.name,
        env.namespace,
        if params.jobType == "datagen" then
          [
            $.tfJobReplica("MASTER", params.numMaster, $.getDatagenCmd(params), workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
          ]
        else if params.jobType == "exporter" then
          [
            $.tfJobReplica("MASTER", params.numMaster, $.getExporterCmd(params), workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
          ]
        else
          [
            $.tfJobReplica("MASTER", params.numMaster, cmd.master, workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
            $.tfJobReplica("WORKER", params.numWorker, cmd.worker, workerImage, params.numWorkerGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
            $.tfJobReplica("PS", params.numPs, cmd.ps, workerImage, params.numPsGpu,
                            workerImagePullSecrets, workerEnv, workerVolumes, workerVolumeMounts),
          ],
        terminationPolicy
      ),
  },
}
