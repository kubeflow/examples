// Component to train a model.
//
// Parameters are used to control training
//   image: Docker iamge to use
//   modelDir: Location to write the model this can be a local path (e.g. to a PV)
//             or it can be any filesystem URI that TF understands (e.g GCS, S3, HDFS)
//   exportDir: Location to export the model
//   trainSteps: Number of training steps to run
//   batchSize: Batch size
//   learningRate: Learning rate
//   envVariables: Comma separated list of environment variables to set.
//     Use this to set environment variables needed to configure S3 access.
//   numWorkers: Number of workers
//   numPs: Number of parameter servers
//
local k = import "k.libsonnet";
local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.train;

local util = import "util.libsonnet";

local trainSecrets = util.parseSecrets(params.secretKeyRefs);

local secretPieces = std.split(params.secret, "=");
local secretName = if std.length(secretPieces) > 0 then secretPieces[0] else "";
local secretMountPath = if std.length(secretPieces) > 1 then secretPieces[1] else "";

local replicaSpec = {
  containers: [
    {
      command: [
        "/usr/bin/python",
        "/opt/model.py",
      ],
      args: [
        "--tf-model-dir=" + params.modelDir,
        "--tf-export-dir=" + params.exportDir,
        "--tf-train-steps=" + params.trainSteps,
        "--tf-batch-size=" + params.batchSize,
        "--tf-learning-rate=" + params.learningRate,
      ],
      env: util.parseEnv(params.envVariables) + trainSecrets,
      image: params.image,
      name: "tensorflow",
      volumeMounts: if secretMountPath != "" then
        [
          {
            name: secretName,
            mountPath: secretMountPath,
            readOnly: true,
          },
        ] else if params.pvcName != "null" && params.pvcName != "" then
        [
          {
            name: "local-storage",
            mountPath: "/mnt",
          },
        ] else [],
      workingDir: "/opt",
    },
  ],
  volumes:
    if secretName != "" then
      [
        {
          name: secretName,
          secret: {
            secretName: secretName,
          },
        },
      ] else if params.pvcName != "null" && params.pvcName != "" then
      [
        {
          name: "local-storage",
          persistentVolumeClaim: {
            claimName: params.pvcName,
          },
        },
      ] else [],
  restartPolicy: "OnFailure",
};


local tfjob = {
  apiVersion: "kubeflow.org/v1beta1",
  kind: "TFJob",
  metadata: {
    name: params.name,
    namespace: env.namespace,
  },
  spec: {
    tfReplicaSpecs: {
      Chief: {
        replicas: 1,
        template: {
          spec: replicaSpec,
        },
      },
      [if params.numWorkers > 0 then "Worker"]: {
        replicas: params.numWorkers,
        template: {
          spec: replicaSpec,
        },
      },
      [if params.numWorkers > 0 then "Ps"]: {
        replicas: params.numPs,
        template: {
          spec: replicaSpec,
        },
      },
    },
  },
};

k.core.v1.list.new([
  tfjob,
])
