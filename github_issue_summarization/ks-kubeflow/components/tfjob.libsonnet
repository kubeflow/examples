{
  parts(params):: {
    apiVersion: "kubeflow.org/v1alpha1",
    kind: "TFJob",
    metadata: {
      name: "tf-job-issue-summarization",
      namespace: params.namespace,
    },
    spec: {
      replicaSpecs: [
        {
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
                      value: "/secret/gcp-credentials/key.json",
                    },
                  ],
                },
              ],
              volumes: [
                {
                  name: "gcp-credentials",
                  secret: {
                    secretName: "gcp-credentials",
                  },
                },
              ],
              restartPolicy: "OnFailure",
            },
          },
          tfReplicaType: "MASTER",
        },
      ],
      terminationPolicy: {
        chief: {
          replicaIndex: 0,
          replicaName: "MASTER",
        },
      },
    },
  },
}
