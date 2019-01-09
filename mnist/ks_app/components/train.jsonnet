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

// The code currently uses environment variables to control the training.
local trainEnv = [
  {
    name: "TF_MODEL_DIR",
    value: params.modelDir,
  },
  {
    name: "TF_EXPORT_DIR",
    value: params.exportDir,
  },
  {
    name: "TF_TRAIN_STEPS",
    value: std.toString(params.trainSteps),
  },
  {
    name: "TF_BATCH_SIZE",
    value: std.toString(params.batchSize),
  },
  {
    name: "TF_LEARNING_RATE",
    value: std.toString(params.learningRate),
  },
];

local secretName = std.split(params.secret, "=")[0];
local secretMountPath = std.split(params.secret, "=")[1];

local replicaSpec = {
  containers: [
    {
      command: [
        "/usr/bin/python",
        "/opt/model.py",
      ],
      env: trainEnv + util.parseEnv(params.envVariables),
      image: params.image,
      name: "tensorflow",
      volumeMounts: if secretMountPath != "" then
        [
          {
            name: secretName,
            mountPath: secretMountPath,
            readOnly: true,
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
