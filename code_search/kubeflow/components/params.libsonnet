{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
    t2tWorkingDir: "gs://kubeflow-examples/t2t-code-search/20180802",
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "t2t-job": {
      jobType: "trainer",

      numWorker: 1,
      numPs: 0,
      numWorkerGpu: 0,
      numPsGpu: 0,

      train_steps: 100,
      eval_steps: 10,

      image: "gcr.io/kubeflow-dev/code-search:v20180802-c622aac",
      imageGpu: "gcr.io/kubeflow-dev/code-search:v20180802-c622aac-gpu",
      imagePullSecrets: [],

      dataDir: "null",
      outputDir: "null",
      model: "null",
      hparams_set: "null",
    },

    "t2t-code-search-datagen": {
      jobType: "datagen",

      name: "t2t-code-search-datagen",

      problem: "github_function_docstring",
      dataDir: $.global.t2tWorkingDir + "/data",
    },

    "t2t-code-search-trainer": {
      jobType: "trainer",

      name: "t2t-code-search-trainer",

      problem: "github_function_docstring",
      dataDir: $.global.t2tWorkingDir + "/data",
      outputDir: $.global.t2tWorkingDir + "/output",
      model: "similarity_transformer",
      hparams_set: "transformer_tiny",
    },

    "t2t-code-search-exporter": {
      jobType: "exporter",

      name: "t2t-code-search-exporter",

      problem: "github_function_docstring",
      dataDir: $.global.t2tWorkingDir + "/data",
      outputDir: $.global.t2tWorkingDir + "/output",
      model: "similarity_transformer",
      hparams_set: "transformer_tiny",
    },

    "t2t-code-search-serving": {
      name: "t2t-code-search",

      modelName: "t2t-code-search",
      modelPath: $.global.t2tWorkingDir + "/output/export/Servo",
      modelServerImage: "gcr.io/kubeflow-images-public/tensorflow-serving-1.8:latest",
      cloud: "gcp",
      gcpCredentialSecretName: "user-gcp-sa",
    },

    "nmslib": {
      replicas: 1,
      image: "gcr.io/kubeflow-dev/code-search-ui:v20180803-156710e",

      problem: "null",
      dataDir: "null",
      lookupFile: "null",
      indexFile: "null",
      servingUrl: "null",
    },

    "search-index-creator": {
      name: "search-index-creator",

      dataDir: $.global.t2tWorkingDir + "/data",
      lookupFile: $.global.t2tWorkingDir + "/code_search_index.csv",
      indexFile: $.global.t2tWorkingDir + "/code_search_index.nmslib",
    },

    "search-index-server": {
      name: "search-index-server",

      problem: "github_function_docstring",
      dataDir: $.global.t2tWorkingDir + "/data",
      lookupFile: $.global.t2tWorkingDir + "/code_search_index.csv",
      indexFile: $.global.t2tWorkingDir + "/code_search_index.nmslib",
      servingUrl: "http://t2t-code-search.kubeflow:8000/v1/models/t2t-code-search:predict",
    },
  },
}
