{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "t2t-job": {
      jobType: "trainer",

      numMaster: 1,
      numWorker: 0,
      numPs: 0,
      numWorkerGpu: 0,
      numPsGpu: 0,

      train_steps: 100,
      eval_steps: 10,

      image: "gcr.io/kubeflow-dev/code-search:v20180719-f04a4b7",
      imageGpu: "gcr.io/kubeflow-dev/code-search:v20180719-gpu-9b8b4a8",
      imagePullSecrets: [],

      dataDir: "null",
      outputDir: "null",
      model: "null",
      hparams_set: "null",
    },

    "t2t-code-search-trainer": {
      jobType: "trainer",
      numWorker: 2,
      numPs: 1,
      // numWorkerGpu: 1,
      // numPsGpu: 1,

      name: "t2t-code-search-trainer",

      problem: "github_function_docstring",
      dataDir: "gs://kubeflow-examples/t2t-code-search/data",
      outputDir: "gs://kubeflow-examples/t2t-code-search/output",
      model: "similarity_transformer",
      hparams_set: "transformer_tiny",
    },

    "t2t-code-search-exporter": {
      jobType: "exporter",

      name: "t2t-code-search-exporter",

      problem: "github_function_docstring",
      dataDir: "gs://kubeflow-examples/t2t-code-search/data",
      outputDir: "gs://kubeflow-examples/t2t-code-search/output",
      model: "similarity_transformer",
      hparams_set: "transformer_tiny",
    },

    "t2t-code-search-serving": {
      name: "t2t-code-search",

      modelName: "t2t_code_search",
      modelPath: "gs://kubeflow-examples/t2t-code-search/output/export/Servo",
      modelServerImage: "gcr.io/kubeflow-images-public/tensorflow-serving-1.8:latest",
      cloud: "gcp",
      gcpCredentialSecretName: "gcp-credentials",
    },

    "nmslib": {
      name: null,
      replicas: 1,
      image: "gcr.io/kubeflow-dev/code-search:v20180621-266e689",

      dataFile: null,
      indexFile: null,
      problem: null,
      dataDir: null,
      servingUrl: null,
    },

    "nms-creator": {
      name: "nms-creator",
    },

    "nms-server": {
      name: "nms-server",
    },
  },
}
