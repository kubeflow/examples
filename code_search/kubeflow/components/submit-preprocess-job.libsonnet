{
  parts(params, env):: {
  	// Submit a Dataflow job to preprocess the github public dataset
    job:: {
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: params.name + '-' + params.jobNameSuffix,
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
                name: "dataflow",
                image: params.image,
                command: [
                  "python2",
                  "-m",
                  "code_search.dataflow.cli.preprocess_github_dataset",
                  "--runner=DataflowRunner",
                  "--project=" + params.project,
                  "--token_pairs_table=" + params.tokenPairsBQTable,
                  "--failed_tokenize_table=" + params.failedTokenizeBQTable,
                  "--data_dir=" + params.dataDir,
                  "--job_name=" + params.jobName + '-' + params.jobNameSuffix,
                  "--temp_location=" + params.workingDir + "/dataflow/temp",
                  "--staging_location=" + params.workingDir + "/dataflow/staging",
                  "--worker_machine_type=" + params.workerMachineType,
                  "--num_workers=" + params.numWorkers,
                  "--requirements_file=requirements.dataflow.txt",
                  if (params.waitUntilFinish == "true") then
                      "--wait_until_finished"
                  else [],
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
  }, // parts
}