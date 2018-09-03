{
  parts(params, env):: {
    // Define some defaults.
    local updatedParams = {
      cloud: "gke",

      dataDir: "gs://kubeflow-demo-base/featurization/yelp-data",
      usrDir: "./yelp_sentiment",
      problem: "yelp_sentiment",

      model: "transformer_encoder",
      hparams: "transformer_yelp_sentiment",
      hparamsSet: "transformer_yelp_sentiment",

      outputGCSPath: "gs://kubeflow-demo-base/training/yelp-model-TPU",

      cpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-cpu:latest",
      gpuImage: "gcr.io/kubeflow-demo-base/kubeflow-yelp-demo-gpu:latest",

      trainSteps: 1000,
      evalSteps: 10,

      tpus: 8,

      jobName: "t2ttpu-v1alpha1",

      tpuEndpoint: "$(KUBE_GOOGLE_CLOUD_TPU_ENDPOINTS)"
    } + params,

    local cloud = std.toString(updatedParams.cloud),

    job:: {
      apiVersion: "kubeflow.org/v1alpha1",
      kind: "TFJob",
      metadata: {
        name: "sentiment-analysis-tpu",
        namespace: env.namespace,
      },
      spec: {
        replicaSpecs: [
          {
            replicas: 1,
            tfReplicaType: "MASTER",
            template: {
              metadata: {
                annotations: {
                  "tf-version.cloud-tpus.google.com": "1.7",
                },
              },
              spec: {
                containers: [
                  {
                    args: [
                      "--model=" + updatedParams.model,
                      "--hparams_set=" + updatedParams.hparamsSet,
                      "--problem=" + updatedParams.problem,
		      "--t2t_usr_dir=" + updatedParams.usrDir,
                      "--train_steps=" + updatedParams.trainSteps,
                      "--eval_steps=" + updatedParams.evalSteps,
                      "--data_dir=" + updatedParams.dataDir,
                      "--output_dir=" + updatedParams.outputGCSPath,
                      "--use_tpu",
                      "--master=" + updatedParams.tpuEndpoint,
                    ],
                    command: [
                      "t2t-trainer",
                    ],
                    [if cloud != "gke" then "env"]: [
                      {
                        name: "GOOGLE_APPLICATION_CREDENTIALS",
                        value: "/secret/gcp-credentials/key.json"
                      },
                    ],
                    image: updatedParams.cpuImage,
                    name: "tensorflow",
                    resources: {
                      [if cloud == "gke" then "limits"]: {
                        "cloud-tpus.google.com/v2": updatedParams.tpus,
                      },
                      requests: {
                        memory: "1Gi",
                      },
                    },
                    [if cloud != "gke" then "volumeMounts"]: [
                      {
                        mountPath: "/secret/gcp-credentials",
                        name: "gcp-credentials",
                      },
                    ],
                  },
                ],
                [if cloud != "gke" then "imagePullSecrets"]: [
                  {
                    name: "gcp-registry-credentials",
                  },
                ],
                restartPolicy: "Never",
                [if cloud != "gke" then "volumes"]: [
                  {
                    name: "gcp-credentials",
                    secret: {
                      secretName: "gcp-credentials",
                    },
                  },
                ],
              },
            },
          },
        ],
      },
    },  // job
  },  //parts
}
