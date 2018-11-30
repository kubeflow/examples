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
      name: "tf-serving",
      gcpCredentialSecretName: "user-gcp-sa",
      serviceType: "ClusterIP",
      deployHttpProxy: false,
      modelBasePath: "gs://some/model",
      // modelName is used by the client.
      modelName: "t2t-code-search",
      defaultCpuImage: "tensorflow/serving:1.11.1",
      defaultGpuImage: "tensorflow/serving:1.11.1-gpu",
      httpProxyImage: "gcr.io/kubeflow-images-public/tf-model-server-http-proxy:v20180723",
      numGpus: "0",
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
      servingUrl: "http://t2t-code-search.kubeflow:8500/v1/models/t2t-code-search:predict",
      // 1 replica is convenient for debugging but we should bump after debugging.
      replicas: 1,
      image: "gcr.io/kubeflow-examples/code-search-ui:v20181122-dc0e646-dirty-043a63",
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
