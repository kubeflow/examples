local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["tfjob-v1alpha2"];

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;

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
          spec: {
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
                ],
                command: [
                  "python",
                ],
                args: [
                  "/workdir/train.py",
                  "--sample_size=" + std.toString(params.sample_size),
                  "--input_data_gcs_bucket=" + params.input_data_gcs_bucket,
                  "--input_data_gcs_path=" + params.input_data_gcs_path,
                  "--output_model_gcs_bucket=" + params.output_model_gcs_bucket,
                  "--output_model_gcs_path=" + params.output_model_gcs_path,
                ],
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
            ],
            restartPolicy: "OnFailure",
          },  // spec
        },  // template
      },  // master
    },  // tfReplicaSpecs
  },  // spec
};

k.core.v1.list.new([
  tfjob,
])
