{
  parts(params, env):: {
    job: {
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: params.name,
        namespace: env.namespace,
        labels: {
          app: params.name,
        },
      },
      spec: {
        replicas: 1,
        template: {
          metadata: {
            labels: {
              app: params.name,
            },
          },
          spec: {
            // Don't restart because all the job should do is launch the Dataflow job.
            restartPolicy: "Never",
            containers: [
              {
                name: "exporter",
                image: params.image,
                command: [
                  "t2t-exporter",
                  "--problem=" + params.problem,
                  "--data_dir=" + params.dataDir,
                  // TODO(jlewi): If we specify checkpoint path then we can specify a particular
                  // checkpoint. Does this then allow us to specify a different directory for outputDir?
                  "--output_dir=" + params.outputDir,
                  "--model=" + params.model,
                  "--hparams_set=" + params.hparams_set,
                  // Need to import the problems.
                  "--t2t_usr_dir=/src/code_search/t2t",
                ],
                env: [
                  {
                    name: "GOOGLE_APPLICATION_CREDENTIALS",
                    value: "/secret/gcp-credentials/user-gcp-sa.json",
                  },
                ],
                workingDir: "/src",
                volumeMounts: [
                  {
                    mountPath: "/secret/gcp-credentials",
                    name: "gcp-credentials",
                  },
                ],  //volumeMounts
              },
            ],  // containers
            volumes: [
              {
                name: "gcp-credentials",
                secret: {
                  secretName: "user-gcp-sa",
                },
              },
            ],
          },  // spec
        },
      },
    },
  },  // parts
}
