{
  global: {},
  components: {

    // TODO(jlewi): t2t-job and t2t-code-search are intended to set values
    // which are reused in different components. Unfortunately, if we
    // override those values for a specific environment, those overrides
    // are not picked up by the individual components.
    // Need to see if we can find a way to fix this.

    local imageTag = "v20181117-3c030ae-dirty-4d809c",
    "t2t-job": {
      jobType: "trainer",
      numChief: 0,
      numWorker: 1,
      numPs: 0,
      numWorkerGpu: 0,
      numPsGpu: 0,
      train_steps: 100,
      eval_steps: 10,
      image: "gcr.io/kubeflow-examples/code-search:" + imageTag,
      imageGpu: "gcr.io/kubeflow-examples/code-search-gpu:" + imageTag,
      dataflowImage: "gcr.io/kubeflow-examples/code-search-dataflow:" + imageTag,

      imagePullSecrets: [],
      // TODO(jlewi): dataDir doesn't seem to be used.
      dataDir: "null",
      outputDir: "null",
      model: "null",
      hparams_set: "null",
    },
    "t2t-code-search": {
      name: "t2t-code-search",
      workingDir: "gs://example/prefix",
      problem: "kf_github_function_docstring",
      model: "kf_similarity_transformer",
      hparams_set: "transformer_tiny",
    },
    "t2t-code-search-datagen": {
      jobType: "datagen",
      name: "t2t-code-search-datagen",
      image: $.components["t2t-job"].image,
      problem: $.components["t2t-code-search"].problem,
      dataDir: $.components["t2t-code-search"].workingDir + "/data",
    },
    "t2t-code-search-trainer": {
      jobType: "trainer",
      name: "t2t-code-search-trainer",
      problem: $.components["t2t-code-search"].problem,
      dataDir: $.components["t2t-code-search"].workingDir + "/data",
      outputDir: $.components["t2t-code-search"].workingDir + "/output",
      model: $.components["t2t-code-search"].model,
      hparams_set: $.components["t2t-code-search"].hparams_set,
    },
    "t2t-code-search-exporter": {
      jobType: "exporter",
      name: "t2t-code-search-exporter",
      problem: $.components["t2t-code-search"].problem,
      dataDir: $.components["t2t-code-search"].workingDir + "/data",
      outputDir: $.components["t2t-code-search"].workingDir + "/output",
      model: $.components["t2t-code-search"].model,
      hparams_set: $.components["t2t-code-search"].hparams_set,
      image: $.components["t2t-job"].image,
    },
    "t2t-code-search-serving": {
      name: "t2t-code-search",
      modelName: "t2t-code-search",
      modelPath: $.components["t2t-code-search"].workingDir + "/output/export/Servo",
      modelServerImage: "gcr.io/kubeflow-images-public/tensorflow-serving-1.8:latest",
      cloud: "gcp",
      gcpCredentialSecretName: "user-gcp-sa",
    },
    nmslib: {
      replicas: 1,
      image: "gcr.io/kubeflow-dev/code-search-ui:v20180817-0d4a60d",
      problem: "null",
      dataDir: "null",
      lookupFile: "null",
      indexFile: "null",
      servingUrl: "null",
    },
    "search-index-creator": {
      name: "search-index-creator",
      dataDir: $.components["t2t-code-search"].workingDir + "/data",
      lookupFile: $.components["t2t-code-search"].workingDir + "/code_search_index.csv",
      indexFile: $.components["t2t-code-search"].workingDir + "/code_search_index.nmslib",
    },
    "search-index-server": {
      name: "search-index-server",
      problem: $.components["t2t-code-search"].problem,
      dataDir: $.components["t2t-code-search"].workingDir + "/data",
      lookupFile: $.components["t2t-code-search"].workingDir + "/code_search_index.csv",
      indexFile: $.components["t2t-code-search"].workingDir + "/code_search_index.nmslib",
      servingUrl: "http://t2t-code-search.kubeflow:9001/v1/models/t2t-code-search:predict",
    },
    "submit-preprocess-job": {
      name: "submit-preprocess-job",
      image: $.components["t2t-job"].dataflowImage,
      targetDataset: "code_search",
      workingDir: $.components["t2t-code-search"].workingDir,
      dataDir: self.workingDir + "/data",
      jobName: "github-preprocess-1104-1831",
      workerMachineType: "n1-highcpu-32",
      // This should be the GitHub table containing the paths and contents.
      githubTable: "",
      numWorkers: 5,
      project: "",
    },
    "submit-code-embeddings-job": {
      name: "submit-code-embeddings-job",
      image: $.components["t2t-job"].dataflowImage,
      // Big query table where results will be written.
      targetDataset: "code_search",
      workingDir: $.components["t2t-code-search"].workingDir,
      dataDir: self.workingDir + "/data",
      // Directory where the model is stored.
      modelDir: "",
      jobName: "submit-code-embeddings-job",
      workerMachineType: "n1-highcpu-32",
      numWorkers: 5,
      project: "",
    },

    tensorboard: {
      image: "tensorflow/tensorflow:1.8.0",
      logDir: "gs://example/to/model/logdir",
      name: "tensorboard",
    },

    "demo-tensorboard": {
      image: "tensorflow/tensorflow:1.11.0",
    },
  },
}
