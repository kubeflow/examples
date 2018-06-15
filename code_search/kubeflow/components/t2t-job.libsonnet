local tfJob = import "kubeflow/tf-job/tf-job.libsonnet";
local baseParams = std.extVar("__ksonnet/params").components["t2t-job"];

{
  parts(newParams, env):: {
    local params = baseParams + newParams,

    local t2tCmd = {
      datagen: [
        "t2t-datagen",
        "--problem=" + params.problem,
        "--data_dir=" + params.dataDir,
      ],

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

    local terminationPolicy = if params.numMaster == 1
                              then tfJob.parts.tfJobTerminationPolicy("MASTER", 0)
                              else tfJob.parts.tfJobTerminationPolicy("WORKER", 0),

    local workerImage = if params.numWorkerGpu > 0 then params.imageGpu else params.image,
    local psImage = if params.numPsGpu > 0 then params.imageGpu else params.image,

    job::
      tfJob.parts.tfJob(
        params.name,
        env.namespace,
        [
          tfJob.parts.tfJobReplica("MASTER", params.numMaster, t2tCmd.master, workerImage, params.imagePullSecrets, params.numWorkerGpu),
          tfJob.parts.tfJobReplica("WORKER", params.numWorker, t2tCmd.worker, workerImage, params.imagePullSecrets, params.numWorkerGpu),
          tfJob.parts.tfJobReplica("PS", params.numPs, t2tCmd.ps, psImage, params.imagePullSecrets, params.numPsGpu),
        ],
        terminationPolicy
      ),
  },
}
