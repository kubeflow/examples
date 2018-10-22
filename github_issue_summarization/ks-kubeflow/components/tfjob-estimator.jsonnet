// This version uses Keras with tf.estimator
local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["tfjob-estimator"];

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;

local podSpec = {
  containers: [
    {
      image: params.image,
      name: "tensorflow",
      volumeMounts: [
        {
          name: "gcp-credentials",
          mountPath: "/secret/gcp-credentials",
          readOnly: true,
        },
        {
          name: "shared-fs",
          mountPath: params.mountPath,
        },
      ],
      command: [
        "python",
        "/issues/train.py",
        "--data_dir=" + params.dataDir,
        "--data_file=" + params.dataFile,
        "--model_dir=" + params.modelDir,
      ],
      //command: [
      //  "tail",
      //  "-f",
      //  "/dev/null",
      //],
      env: [
        {
          name: "GOOGLE_APPLICATION_CREDENTIALS",
          value: "/secret/gcp-credentials/" + params.gcpSecretFile,
        },
      ],
    },
  ],
  volumes: [
    {
      name: "gcp-credentials",
      secret: {
        secretName: params.gcpSecretName,
      },
    },
    {
      name: "shared-fs",
      persistentVolumeClaim: {
        claimName: params.pvc,
      },
    },
  ],
  restartPolicy: "OnFailure",
};  // spec

local workerSpec = if params.numWorkers > 0 then
  { Worker:
    {
      replicas: 5,
      template: {
        spec: podSpec,  // spec
      },  // template
    } }
else {};


local psSpec = if params.numPs > 0 then
  { Ps: {
    replicas: 3,
    template: {
      spec: podSpec,  // spec
    },  // template
  } } else {};  //  ps

local tfjob = {
  apiVersion: "kubeflow.org/v1alpha2",
  kind: "TFJob",
  metadata: {
    name: name,
    namespace: namespace,
  },
  spec: {
    tfReplicaSpecs: {
      Master: {
        replicas: 1,
        template: {
          spec: podSpec,  // spec
        },  // template
      },  // master
    } + workerSpec + psSpec,
    // tfReplicaSpecs
  },  // spec
};

k.core.v1.list.new([
  tfjob,
])
